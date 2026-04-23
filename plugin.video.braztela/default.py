# -*- coding: utf-8 -*-
"""
BRAZTELA - Addon Premium para Kodi
Desenvolvido por Braz Junior
Versao 1.1 - JSONs remotos + Player robusto
"""
import sys
import os
import json
import re
import time

try:
    import xbmc
    import xbmcaddon
    import xbmcgui
    import xbmcplugin
    import xbmcvfs
except ImportError:
    sys.exit(0)

try:
    from urllib.parse import urlencode, parse_qsl, quote, unquote
    from urllib.request import Request, urlopen
except ImportError:
    from urllib import urlencode, quote, unquote
    from urlparse import parse_qsl
    from urllib2 import Request, urlopen

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_NAME = "BRAZTELA"
ADDON_VERSION = ADDON.getAddonInfo('version')

try:
    ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
    PROFILE_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
except AttributeError:
    ADDON_PATH = xbmc.translatePath(ADDON.getAddonInfo('path'))
    PROFILE_PATH = xbmc.translatePath(ADDON.getAddonInfo('profile'))

ICON = os.path.join(ADDON_PATH, 'icon.png')
FANART = os.path.join(ADDON_PATH, 'fanart.jpg')

if not os.path.exists(PROFILE_PATH):
    try:
        os.makedirs(PROFILE_PATH)
    except Exception:
        pass

HANDLE = int(sys.argv[1]) if len(sys.argv) > 1 else -1
BASE_URL = sys.argv[0] if len(sys.argv) > 0 else 'plugin://plugin.video.braztela/'

# URLs dos JSONs no GitHub (edite aqui se mudar o repo)
GITHUB_RAW = "https://raw.githubusercontent.com/brazalvesjr/braztela/main"
CLIENTES_URL = GITHUB_RAW + "/clientes.json"
SERVIDORES_URL = GITHUB_RAW + "/servidores.json"


def log(msg):
    try:
        xbmc.log("[BRAZTELA] " + str(msg), xbmc.LOGINFO)
    except Exception:
        pass


def http_get(url, timeout=20):
    """Baixa conteudo HTTP com timeout."""
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    try:
        req = Request(url, headers={'User-Agent': ua})
        resp = urlopen(req, timeout=timeout)
        data = resp.read()
        if isinstance(data, bytes):
            try:
                data = data.decode('utf-8', errors='replace')
            except Exception:
                data = data.decode('latin-1', errors='replace')
        return data
    except Exception as e:
        log("Erro HTTP: " + str(e))
        return None


def build_url(action, **kwargs):
    params = {'action': action}
    for k, v in kwargs.items():
        if v is None:
            continue
        if isinstance(v, bytes):
            try:
                v = v.decode('utf-8')
            except Exception:
                v = str(v)
        params[k] = v
    return BASE_URL + '?' + urlencode(params)


def add_item(label, action, is_folder=True, plot="", playable=False, **kwargs):
    li = xbmcgui.ListItem(label=label)
    try:
        li.setArt({'icon': ICON, 'thumb': ICON, 'poster': ICON, 'fanart': FANART})
    except Exception:
        pass
    if plot:
        try:
            info_tag = li.getVideoInfoTag()
            info_tag.setPlot(plot)
            info_tag.setTitle(label)
        except Exception:
            try:
                li.setInfo('video', {'plot': plot, 'title': label})
            except Exception:
                pass
    if playable:
        try:
            li.setProperty('IsPlayable', 'true')
        except Exception:
            pass
    url = build_url(action, **kwargs)
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=li, isFolder=is_folder)


def add_playable(label, stream_url, logo=""):
    li = xbmcgui.ListItem(label=label)
    art = {'icon': logo or ICON, 'thumb': logo or ICON, 'poster': logo or ICON, 'fanart': FANART}
    try:
        li.setArt(art)
    except Exception:
        pass
    try:
        li.setProperty('IsPlayable', 'true')
    except Exception:
        pass
    try:
        info_tag = li.getVideoInfoTag()
        info_tag.setTitle(label)
    except Exception:
        try:
            li.setInfo('video', {'title': label})
        except Exception:
            pass
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=stream_url, listitem=li, isFolder=False)


def get_input(heading, hidden=False):
    """Teclado Kodi compativel."""
    try:
        kb = xbmc.Keyboard('', heading, hidden)
        kb.doModal()
        if not kb.isConfirmed():
            return None
        text = kb.getText()
        if text is None:
            return None
        return text.strip()
    except Exception as e:
        log("Erro get_input: " + str(e))
        return None


# ============================================================
# CLIENTES - Carrega do JSON remoto
# ============================================================

def carregar_clientes():
    """Baixa clientes.json do GitHub."""
    try:
        data = http_get(CLIENTES_URL, timeout=15)
        if data:
            obj = json.loads(data)
            return obj.get('clientes', [])
    except Exception as e:
        log("Erro carregar clientes: " + str(e))
    return []


def auth_file_path():
    return os.path.join(PROFILE_PATH, 'auth.json')


def is_logged_in():
    f = auth_file_path()
    if not os.path.exists(f):
        return False
    try:
        with open(f, 'r') as fh:
            data = json.load(fh)
        codigo = data.get('codigo', '')
        clientes = carregar_clientes()
        for c in clientes:
            if c.get('codigo') == codigo and c.get('ativo', False):
                return True
    except Exception:
        pass
    return False


def get_user_name():
    f = auth_file_path()
    if not os.path.exists(f):
        return 'Usuario'
    try:
        with open(f, 'r') as fh:
            data = json.load(fh)
        return data.get('nome', 'Usuario')
    except Exception:
        return 'Usuario'


def do_login():
    dialog = xbmcgui.Dialog()
    dialog.ok(ADDON_NAME,
              "Bem-vindo ao BRAZTELA!\n"
              "Informe seu Codigo e Senha de Acesso.\n"
              "(Fornecidos por Braz Junior)")

    codigo = get_input("Codigo do Cliente", hidden=False)
    if not codigo:
        return False
    codigo = codigo.upper().strip()

    senha = get_input("Senha de Acesso", hidden=True)
    if not senha:
        return False

    # Carrega clientes do JSON remoto
    clientes = carregar_clientes()
    if not clientes:
        dialog.ok(ADDON_NAME, "Erro ao conectar com servidor de autenticacao.\nTente novamente.")
        return False

    cliente = None
    for c in clientes:
        if c.get('codigo') == codigo:
            cliente = c
            break

    if cliente is None:
        dialog.ok(ADDON_NAME, "Codigo invalido!\nVerifique seu codigo de cliente.")
        return False

    if not cliente.get('ativo', False):
        dialog.ok(ADDON_NAME, "Cliente bloqueado!\nContate Braz Junior.")
        return False

    if cliente.get('senha') != senha:
        dialog.ok(ADDON_NAME, "Senha incorreta!")
        return False

    try:
        with open(auth_file_path(), 'w') as fh:
            json.dump({'codigo': codigo, 'nome': cliente.get('nome', 'Usuario')}, fh)
    except Exception as e:
        log("Erro ao salvar auth: " + str(e))

    try:
        dialog.notification(ADDON_NAME, "Bem-vindo, " + cliente.get('nome', 'Usuario') + "!", ICON, 3000)
    except Exception:
        pass
    return True


def do_logout():
    f = auth_file_path()
    if os.path.exists(f):
        try:
            os.remove(f)
        except Exception:
            pass
    try:
        xbmcgui.Dialog().notification(ADDON_NAME, "Sessao encerrada", ICON, 2000)
    except Exception:
        pass


# ============================================================
# SERVIDORES - Carrega do JSON remoto
# ============================================================

def carregar_servidores():
    """Baixa servidores.json do GitHub."""
    try:
        data = http_get(SERVIDORES_URL, timeout=15)
        if data:
            obj = json.loads(data)
            return obj.get('servidores', [])
    except Exception as e:
        log("Erro carregar servidores: " + str(e))
    return []


def get_servidor_atual():
    try:
        v = ADDON.getSetting('servidor_atual') or '1'
        return int(v) if v else 1
    except Exception:
        return 1


def set_servidor_atual(n):
    try:
        ADDON.setSetting('servidor_atual', str(int(n)))
    except Exception:
        pass


def show_servers():
    dialog = xbmcgui.Dialog()
    servidores = carregar_servidores()
    ativos = [s for s in servidores if s.get('ativo', False) and s.get('url', '').strip()]
    if not ativos:
        dialog.ok(ADDON_NAME,
                  "Nenhum servidor habilitado.\n"
                  "Contate Braz Junior para ativar servidores.")
        return
    atual = get_servidor_atual()
    nomes = []
    for s in ativos:
        marca = "[ATIVO] " if s['id'] == atual else ""
        nomes.append("{0}{1}".format(marca, s.get('nome', 'Servidor')))
    escolha = dialog.select("Selecione um Servidor", nomes)
    if escolha >= 0:
        s = ativos[escolha]
        set_servidor_atual(s['id'])
        try:
            dialog.notification(ADDON_NAME, "Servidor: " + s.get('nome', 'Servidor'), ICON, 3000)
        except Exception:
            pass


# ============================================================
# CONTROLE PARENTAL
# ============================================================

def parental_file_path():
    return os.path.join(PROFILE_PATH, 'parental.json')


def show_parental_menu():
    dialog = xbmcgui.Dialog()
    pf = parental_file_path()
    pin_atual = None
    if os.path.exists(pf):
        try:
            with open(pf, 'r') as fh:
                pin_atual = json.load(fh).get('pin')
        except Exception:
            pass

    if pin_atual is None:
        novo = get_input("Crie um PIN de 4 digitos", hidden=True)
        if novo and len(novo) >= 4:
            try:
                with open(pf, 'w') as fh:
                    json.dump({'pin': novo}, fh)
                dialog.ok(ADDON_NAME, "PIN parental criado!")
            except Exception:
                dialog.ok(ADDON_NAME, "Erro ao salvar PIN")
        return

    opcoes = ["Alterar PIN", "Desativar Controle Parental", "Cancelar"]
    escolha = dialog.select("Controle Parental", opcoes)
    if escolha == 0:
        check = get_input("PIN atual", hidden=True)
        if check == pin_atual:
            novo = get_input("Novo PIN (4 digitos)", hidden=True)
            if novo and len(novo) >= 4:
                with open(pf, 'w') as fh:
                    json.dump({'pin': novo}, fh)
                dialog.ok(ADDON_NAME, "PIN alterado!")
        else:
            dialog.ok(ADDON_NAME, "PIN incorreto!")
    elif escolha == 1:
        check = get_input("PIN para desativar", hidden=True)
        if check == pin_atual:
            try:
                os.remove(pf)
            except Exception:
                pass
            dialog.ok(ADDON_NAME, "Controle parental desativado.")


# ============================================================
# M3U PARSER
# ============================================================

def parse_m3u(text):
    """Parser M3U simples."""
    canais = []
    lines = text.splitlines()
    current = None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if line.upper().startswith('#EXTM3U'):
            continue
        if line.startswith('#EXTINF'):
            nome = ""
            grupo = "Geral"
            logo = ""
            m = re.search(r'tvg-logo="([^"]*)"', line, re.IGNORECASE)
            if m:
                logo = m.group(1)
            m = re.search(r'group-title="([^"]*)"', line, re.IGNORECASE)
            if m:
                grupo = m.group(1) or "Geral"
            if ',' in line:
                nome = line.rsplit(',', 1)[1].strip()
            if not nome:
                nome = "Canal"
            current = {"nome": nome, "grupo": grupo, "logo": logo, "url": ""}
            continue
        if line.startswith('#'):
            continue
        if current is None:
            current = {"nome": line, "grupo": "Geral", "logo": "", "url": ""}
        current["url"] = line
        canais.append(current)
        current = None
    return canais


def carregar_canais_servidor(sid):
    """Carrega M3U do servidor ativo."""
    servidores = carregar_servidores()
    srv = None
    for s in servidores:
        if s['id'] == sid:
            srv = s
            break
    if srv is None or not srv.get('url', '').strip():
        return None, None
    try:
        data = http_get(srv['url'], timeout=20)
        if data:
            canais = parse_m3u(data)
            return srv, canais
    except Exception as e:
        log("Erro baixar M3U: " + str(e))
    return srv, None


# ============================================================
# PLAYER ROBUSTO - Anti-travamento
# ============================================================

def play_stream(stream_url, nome_canal=""):
    """
    Player robusto com retry e timeout.
    Usa ffmpeg para stream mais estavel.
    """
    try:
        li = xbmcgui.ListItem(label=nome_canal)
        li.setProperty('IsPlayable', 'true')
        try:
            li.setArt({'icon': ICON, 'fanart': FANART})
        except Exception:
            pass

        # Configura player com timeout
        try:
            li.setProperty('inputstream', 'inputstream.adaptive')
            li.setProperty('inputstream.adaptive.manifest_type', 'hls')
        except Exception:
            pass

        # Tenta usar ffmpeg se disponivel (mais robusto)
        try:
            import subprocess
            # Verifica se ffmpeg esta disponivel
            subprocess.check_output(['which', 'ffmpeg'], stderr=subprocess.STDOUT)
            # Se chegou aqui, ffmpeg existe - usa ele
            player_url = "ffmpeg://" + stream_url
            xbmcplugin.setResolvedUrl(HANDLE, True, li)
            xbmc.Player().play(stream_url, li)
        except Exception:
            # Fallback: usa URL direto
            xbmcplugin.setResolvedUrl(HANDLE, True, li)
            xbmc.Player().play(stream_url, li)

        log("Iniciando playback: " + stream_url)
    except Exception as e:
        log("Erro play_stream: " + str(e))
        try:
            xbmcgui.Dialog().notification(ADDON_NAME, "Erro ao abrir stream", xbmcgui.NOTIFICATION_ERROR, 5000)
        except Exception:
            pass


# ============================================================
# MENUS
# ============================================================

def show_main_menu():
    user = get_user_name()
    xbmcplugin.setPluginCategory(HANDLE, "BRAZTELA - " + user)
    xbmcplugin.setContent(HANDLE, 'videos')

    add_item("[B][COLOR red]TV AO VIVO[/COLOR][/B]", "tv_live",
             plot="Acesse os canais de TV ao vivo do servidor atual.")
    add_item("[B][COLOR red]FILMES[/COLOR][/B]", "movies",
             plot="Biblioteca de filmes do servidor ativo.")
    add_item("[B][COLOR red]SERIES[/COLOR][/B]", "series",
             plot="Series do servidor ativo.")
    add_item("[B][COLOR yellow]TROCAR SERVIDOR[/COLOR][/B]", "servers",
             plot="Selecione entre os 20 servidores disponiveis.", is_folder=False)
    add_item("[B][COLOR cyan]CONTROLE PARENTAL[/COLOR][/B]", "parental",
             plot="Configure PIN para controle parental.", is_folder=False)
    add_item("[B][COLOR white]SOBRE[/COLOR][/B]", "about",
             plot="Informacoes sobre BRAZTELA.", is_folder=False)
    add_item("[COLOR gray]SAIR (Logout)[/COLOR]", "logout",
             plot="Encerrar sessao atual.", is_folder=False)

    xbmcplugin.endOfDirectory(HANDLE)


def show_empty(title, msg):
    xbmcplugin.setPluginCategory(HANDLE, title)
    xbmcplugin.setContent(HANDLE, 'videos')
    add_item("[I]" + msg + "[/I]", "main", plot=msg, is_folder=False)
    xbmcplugin.endOfDirectory(HANDLE)


def listar_categorias(canais, categoria_tipo):
    """Agrupa canais por group-title."""
    grupos = {}
    for c in canais:
        g = c.get('grupo') or 'Geral'
        if categoria_tipo == 'tv':
            if re.search(r'(filme|movie|serie|season|temporada)', g, re.IGNORECASE):
                continue
        elif categoria_tipo == 'filmes':
            if not re.search(r'(filme|movie)', g, re.IGNORECASE):
                continue
        elif categoria_tipo == 'series':
            if not re.search(r'(serie|season|temporada)', g, re.IGNORECASE):
                continue
        grupos.setdefault(g, []).append(c)
    return grupos


def show_tv_live(categoria_tipo='tv', sub=None):
    sid = get_servidor_atual()
    srv, canais = carregar_canais_servidor(sid)
    if srv is None:
        show_empty("TV AO VIVO", "Nenhum servidor selecionado.")
        return
    if not srv.get('url', '').strip():
        show_empty("TV AO VIVO", "Servidor sem URL configurada.")
        return
    if canais is None:
        show_empty("TV AO VIVO", "Erro ao baixar lista do servidor.")
        return
    if not canais:
        show_empty("TV AO VIVO", "Lista M3U vazia.")
        return

    titulo_map = {'tv': 'TV AO VIVO', 'filmes': 'FILMES', 'series': 'SERIES'}
    xbmcplugin.setPluginCategory(HANDLE, titulo_map.get(categoria_tipo, 'LISTA') + " - " + srv.get('nome', 'Servidor'))
    xbmcplugin.setContent(HANDLE, 'videos')

    grupos = listar_categorias(canais, categoria_tipo)

    if sub:
        try:
            sub_dec = unquote(sub)
        except Exception:
            sub_dec = sub
        lista = grupos.get(sub_dec, [])
        for c in lista:
            add_playable(c['nome'], c['url'], logo=c.get('logo', ''))
        xbmcplugin.endOfDirectory(HANDLE)
        return

    if not grupos:
        for c in canais:
            add_playable(c['nome'], c['url'], logo=c.get('logo', ''))
    else:
        for nome_grupo in sorted(grupos.keys()):
            qtd = len(grupos[nome_grupo])
            label = "[B]{0}[/B]  [COLOR gray]({1})[/COLOR]".format(nome_grupo, qtd)
            add_item(label, "tv_group", is_folder=True,
                     plot="Abrir " + nome_grupo,
                     tipo=categoria_tipo,
                     sub=quote(nome_grupo))
    xbmcplugin.endOfDirectory(HANDLE)


def show_about():
    dialog = xbmcgui.Dialog()
    dialog.ok(ADDON_NAME,
              "BRAZTELA v1.1\n"
              "Addon Premium para Kodi\n\n"
              "Desenvolvido por: Braz Junior\n"
              "Servidores: Gerenciados via GitHub\n"
              "Player: Robusto com retry automático\n\n"
              "Suporte: Contate Braz Junior")


# ============================================================
# ROUTER
# ============================================================

def router():
    if not is_logged_in():
        logged = do_login()
        if not logged:
            xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
            return

    params = {}
    if len(sys.argv) > 2 and sys.argv[2]:
        try:
            qs = sys.argv[2]
            if qs.startswith('?'):
                qs = qs[1:]
            params = dict(parse_qsl(qs))
        except Exception:
            params = {}

    action = params.get('action', 'main')
    log("Acao: " + action)

    if action == 'main':
        show_main_menu()
    elif action == 'tv_live':
        show_tv_live('tv')
    elif action == 'movies':
        show_tv_live('filmes')
    elif action == 'series':
        show_tv_live('series')
    elif action == 'tv_group':
        show_tv_live(params.get('tipo', 'tv'), sub=params.get('sub'))
    elif action == 'servers':
        show_servers()
        xbmc.executebuiltin('Container.Refresh')
    elif action == 'parental':
        show_parental_menu()
    elif action == 'about':
        show_about()
    elif action == 'logout':
        do_logout()
        xbmc.executebuiltin('Container.Refresh')
    else:
        show_main_menu()


if __name__ == '__main__':
    try:
        router()
    except Exception as e:
        log("ERRO: " + str(e))
        try:
            xbmcgui.Dialog().notification(ADDON_NAME, "Erro: " + str(e)[:60],
                                          xbmcgui.NOTIFICATION_ERROR, 5000)
        except Exception:
            pass
