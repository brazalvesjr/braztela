# -*- coding: utf-8 -*-
"""
BRAZTELA - Player Avançado Anti-Travamento
Autor: Braz Junior

Estratégias combinadas para evitar travamento e saída do canal:
  1. InputStream Adaptive (HLS/DASH segment-based).
  2. Monitor de reprodução com auto-reconexão em caso de erro/parada
     inesperada (até N tentativas configuráveis).
  3. Fallback de extensão (.m3u8 -> .ts -> .mp4).
  4. Headers HTTP (User-Agent, Referer) via ListItem properties.
  5. advancedsettings.xml otimizado (escrito em runtime).
"""
import sys
import time
import xbmc
import xbmcgui
import xbmcplugin

from . import control, xtream


def _cfg_inputstream():
    return control.setting('use_inputstream') == 'true'


def _cfg_reconnect():
    return control.setting('auto_reconnect') == 'true'


def _cfg_retries():
    try:
        return max(1, int(control.setting('reconnect_tries') or 3))
    except Exception:
        return 3


def _user_agent():
    return control.setting('user_agent') or \
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'


def _build_listitem(title, url, meta=None, is_live=False):
    li = xbmcgui.ListItem(label=title, path=url)

    info = {'title': title}
    if meta:
        if meta.get('plot'):
            info['plot'] = meta['plot']
        if meta.get('year'):
            try:
                info['year'] = int(meta['year'])
            except Exception:
                pass
        if meta.get('rating'):
            try:
                info['rating'] = float(meta['rating'])
            except Exception:
                pass
        if meta.get('duration'):
            try:
                info['duration'] = int(meta['duration'])
            except Exception:
                pass
        if meta.get('genre'):
            info['genre'] = meta['genre']
        if meta.get('cast'):
            cast = meta['cast']
            if isinstance(cast, str):
                cast = [c.strip() for c in cast.split(',') if c.strip()]
            info['cast'] = cast
        if meta.get('director'):
            info['director'] = meta['director']

    li.setInfo('video', info)

    art = {
        'icon': (meta or {}).get('poster') or control.ICON,
        'thumb': (meta or {}).get('poster') or control.ICON,
        'poster': (meta or {}).get('poster') or control.ICON,
        'fanart': (meta or {}).get('fanart') or control.FANART,
    }
    li.setArt(art)

    headers = 'User-Agent={0}'.format(_user_agent().replace(' ', '%20'))

    # InputStream Adaptive para HLS/DASH
    if _cfg_inputstream() and (url.lower().endswith('.m3u8') or is_live):
        try:
            li.setProperty('inputstream', 'inputstream.adaptive')
            # Kodi 19+
            if url.lower().endswith('.m3u8') or '/live/' in url.lower():
                li.setProperty('inputstream.adaptive.manifest_type', 'hls')
            elif '.mpd' in url.lower():
                li.setProperty('inputstream.adaptive.manifest_type', 'mpd')
            li.setProperty('inputstream.adaptive.stream_headers', headers)
            li.setProperty('inputstream.adaptive.manifest_headers', headers)
        except Exception as e:
            control.log('InputStream setup failed: {0}'.format(e))

    li.setProperty('IsPlayable', 'true')
    li.setMimeType('application/vnd.apple.mpegurl' if url.lower().endswith('.m3u8')
                   else ('video/mp4' if url.lower().endswith('.mp4') else 'video/mp2t'))
    li.setContentLookup(False)
    return li


def resolve_and_play(url, title, meta=None, is_live=False):
    """
    Envia ListItem resolvido ao Kodi (modo correto para IsPlayable=true) e
    inicia o monitor de reprodução anti-travamento (reconexão).
    """
    li = _build_listitem(title, url, meta=meta, is_live=is_live)
    try:
        handle = int(sys.argv[1])
        xbmcplugin.setResolvedUrl(handle, True, li)
    except Exception as e:
        control.log('setResolvedUrl fallback: {0}'.format(e))
        xbmc.Player().play(url, li)

    if _cfg_reconnect():
        _BrazMonitor(url, title, meta, is_live).start()


class _BrazMonitor(xbmc.Player):
    """
    Monitor de reprodução que detecta erros/parada abrupta e reinicia o stream
    automaticamente para evitar que o canal saia ou trave.
    """
    def __init__(self, url, title, meta, is_live):
        super().__init__()
        self._url   = url
        self._title = title
        self._meta  = meta or {}
        self._live  = is_live
        self._tries = 0
        self._max   = _cfg_retries()

    def start(self):
        # Espera até o vídeo começar (até 15s)
        waited = 0
        while not self.isPlayingVideo() and waited < 15:
            xbmc.sleep(500)
            waited += 0.5
        control.log('BrazMonitor iniciado ({0})'.format(self._title))
        self._loop()

    def _loop(self):
        monitor = xbmc.Monitor()
        last_time = time.time()
        while not monitor.abortRequested():
            if monitor.waitForAbort(2):
                break
            if self.isPlayingVideo():
                last_time = time.time()
            else:
                # Player parou sem pedido do usuário
                idle = time.time() - last_time
                if idle > 5 and self._tries < self._max:
                    self._tries += 1
                    control.notify(control.ADDON_NAME,
                                   'Reconectando... ({0}/{1})'.format(
                                       self._tries, self._max))
                    control.log('BrazMonitor reconectando {0}/{1}'.format(
                        self._tries, self._max))
                    self._reconnect()
                    last_time = time.time()
                elif self._tries >= self._max:
                    control.notify(control.ADDON_NAME,
                                   'Falha ao reconectar. Tente outro canal.')
                    break

    def _reconnect(self):
        # Tenta variantes de extensão
        variants = [self._url]
        if self._url.endswith('.ts'):
            variants.append(self._url[:-3] + '.m3u8')
        elif self._url.endswith('.m3u8'):
            variants.append(self._url[:-5] + '.ts')
        for u in variants:
            li = _build_listitem(self._title, u, meta=self._meta, is_live=self._live)
            self.play(u, li)
            xbmc.sleep(3000)
            if self.isPlayingVideo():
                return
        control.log('Nenhuma variante funcionou para {0}'.format(self._url))
