# -*- coding: utf-8 -*-
"""
BRAZTELA - Utilitários (HTTP, cache, diretórios)
Autor: Braz Junior
"""
import json
import os
import sys
import time
import gzip
import io
import urllib.parse
import urllib.request
import urllib.error
import xbmcgui
import xbmcplugin

from . import control

CACHE_DIR = os.path.join(control.ADDON_DATA, 'cache')
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)


# =============================================================
#   HTTP
# =============================================================
def http_get(url, timeout=15, headers=None, retries=3):
    """GET robusto com retry, gzip e headers personalizados."""
    default_headers = {
        'User-Agent': control.setting('user_agent') or
                      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    if headers:
        default_headers.update(headers)

    last_exc = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=default_headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
                if resp.headers.get('Content-Encoding') == 'gzip':
                    data = gzip.decompress(data)
                return data.decode('utf-8', errors='replace')
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            last_exc = e
            control.log('http_get retry {0}/{1} {2}: {3}'.format(
                attempt + 1, retries, url, e))
            time.sleep(1.5 ** attempt)
    if last_exc:
        control.log('http_get FAILED: {0}'.format(url))
    return None


def http_json(url, timeout=15, headers=None, retries=3):
    raw = http_get(url, timeout=timeout, headers=headers, retries=retries)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception as e:
        control.log('JSON parse error on {0}: {1}'.format(url, e))
        return None


# =============================================================
#   Cache simples em disco (JSON com TTL)
# =============================================================
def cache_get(key, ttl_minutes=60):
    path = os.path.join(CACHE_DIR, '{0}.json'.format(_safe_name(key)))
    if not os.path.exists(path):
        return None
    try:
        age_min = (time.time() - os.path.getmtime(path)) / 60.0
        if age_min > ttl_minutes:
            return None
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def cache_set(key, value):
    path = os.path.join(CACHE_DIR, '{0}.json'.format(_safe_name(key)))
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(value, f)
    except Exception as e:
        control.log('cache_set error: {0}'.format(e))


def cache_clear():
    try:
        for f in os.listdir(CACHE_DIR):
            try:
                os.remove(os.path.join(CACHE_DIR, f))
            except Exception:
                pass
    except Exception:
        pass


def _safe_name(key):
    return ''.join(c if c.isalnum() else '_' for c in str(key))[:80]


# =============================================================
#   Construção de ListItems para o Kodi
# =============================================================
def _handle():
    try:
        return int(sys.argv[1])
    except Exception:
        return -1


def build_url(params):
    return '{0}?{1}'.format(sys.argv[0], urllib.parse.urlencode(params))


def add_dir(name, params, icon=None, fanart=None, description='',
            is_folder=True, info=None, meta=None):
    """
    Adiciona item de diretório ou playable com suporte completo a metadados
    (sinopse, rating, ano, duração, elenco, gênero, poster, fanart).
    """
    url = build_url(params)
    li = xbmcgui.ListItem(label=name)
    art = {
        'icon':  icon or control.ICON,
        'thumb': icon or control.ICON,
        'poster': (meta or {}).get('poster') or icon or control.ICON,
        'fanart': fanart or (meta or {}).get('fanart') or control.FANART,
        'banner': (meta or {}).get('banner') or icon or control.ICON,
    }
    li.setArt(art)

    info_labels = {'title': name, 'plot': description or ''}
    if info:
        info_labels.update(info)
    if meta:
        if meta.get('year'):
            info_labels['year'] = int(meta['year']) if str(meta['year']).isdigit() else 0
        if meta.get('rating'):
            try:
                info_labels['rating'] = float(meta['rating'])
            except Exception:
                pass
        if meta.get('duration'):
            try:
                info_labels['duration'] = int(meta['duration'])
            except Exception:
                pass
        if meta.get('genre'):
            info_labels['genre'] = meta['genre']
        if meta.get('cast'):
            # cast como lista de strings
            cast = meta['cast']
            if isinstance(cast, str):
                cast = [c.strip() for c in cast.split(',') if c.strip()]
            info_labels['cast'] = cast
        if meta.get('director'):
            info_labels['director'] = meta['director']
        if meta.get('mpaa'):
            info_labels['mpaa'] = meta['mpaa']
        if meta.get('releasedate'):
            info_labels['premiered'] = meta['releasedate']

    li.setInfo('video', info_labels)

    if not is_folder:
        li.setProperty('IsPlayable', 'true')

    # Menu contextual
    cm = [('Informações', 'Action(Info)')]
    li.addContextMenuItems(cm, replaceItems=False)

    xbmcplugin.addDirectoryItem(handle=_handle(), url=url,
                                listitem=li, isFolder=is_folder)


def end_directory(sort=True, content='videos'):
    try:
        xbmcplugin.setContent(_handle(), content)
        if sort:
            xbmcplugin.addSortMethod(_handle(), xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.endOfDirectory(_handle(), succeeded=True, cacheToDisc=False)
    except Exception as e:
        control.log('end_directory: {0}'.format(e))


def get_params():
    """Parse sys.argv[2] (?a=1&b=2) em dict."""
    q = sys.argv[2][1:] if len(sys.argv) > 2 and sys.argv[2] else ''
    out = {}
    if q:
        for pair in q.split('&'):
            if '=' in pair:
                k, v = pair.split('=', 1)
                out[k] = urllib.parse.unquote_plus(v)
    return out
