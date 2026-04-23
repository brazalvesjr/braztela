#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BRAZTELA - Addon Premium para Kodi
Desenvolvido por Braz Junior
Versao 1.2 - URLs diretas de M3U + JSONs remotos
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

# URLs dos JSONs no GitHub
GITHUB_RAW = "https://raw.githubusercontent.com/brazalvesjr/braztela/main"
CLIENTES_URL = GITHUB_RAW + "/clientes.json"
SERVIDORES_URL = GITHUB_RAW + "/servidores.json"


def log(msg):
    try:
        xbmc.log("[BRAZTELA] " + str(msg), xbmc.LOGINFO)
    except Exception:
        pass


def http_get(url, timeout=20):
    """Baixa conteudo HTTP com timeout e retry."""
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    for tentativa in range(3):
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
            log("Erro HTTP (tentativa {0}): {1}".format(tentativa + 1, str(e)))
            if tentativa < 2:
                time.sleep(2)
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
# M3U PARSER - Suporta URLs diretas de M3U
# ============================================================

def parse_m3u(text):
    """Parser M3U robusto para URLs diretas."""
    canais = []
    lines = text.splitlines()
    current = None
    
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        
        # Ignora cabecalho
        if line.upper().startswith('#EXTM3U'):
            continue
        
        # Processa linhas de info
        if line.startswith('#EXTINF'):
            nome = ""
            logo = ""
            
            # Extrai nome (depois da ultima virgula)
            if ',' in line:
                nome = line.split(',', 1)[1].strip()
            
            # Extrai logo (tvg-logo)
            match = re.search(r'tvg-logo="([^"]*)"', line)
            if match:
                logo = match.group(1)
            
            current = {'nome': nome or 'Canal', 'logo': logo}
        
        # Processa URL (linhas que nao comecam com #)
        elif current and not line.startswith('#'):
            current['url'] = line
            canais.append(current)
            current = None
    
    return canais


def listar_canais_tv():
    """Lista canais de TV do servidor ativo."""
    dialog = xbmcgui.Dialog()
    servidores = carregar_servidores()
    
    if not servidores:
        dialog.ok(ADDON_NAME, "Erro ao buscar lista do servidor.")
        return
    
    servidor_id = get_servidor_atual()
    servidor = None
    for s in servidores:
        if s['id'] == servidor_id and s.get('ativo', False):
            servidor = s
            break
    
    if not servidor or not servidor.get('url', '').strip():
        dialog.ok(ADDON_NAME, "Servidor nao configurado.\nEscolha um servidor em TROCAR SERVIDOR.")
        return
    
    # Baixa M3U
    url_m3u = servidor.get('url', '').strip()
    log("Baixando M3U de: " + url_m3u)
    
    pDialog = xbmcgui.DialogProgress()
    pDialog.create(ADDON_NAME, "Carregando canais...")
    
    m3u_data = http_get(url_m3u, timeout=30)
    pDialog.close()
    
    if not m3u_data:
        dialog.ok(ADDON_NAME, "Erro ao buscar lista do servidor.\nVerifique a URL e conexao.")
        return
    
    # Parseia M3U
    canais = parse_m3u(m3u_data)
    
    if not canais:
        dialog.ok(ADDON_NAME, "Nenhum canal encontrado.\nVerifique a URL do servidor.")
        return
    
    # Lista canais
    for canal in canais:
        add_playable(canal['nome'], canal['url'], canal.get('logo', ''))
    
    xbmcplugin.endOfDirectory(HANDLE)


def listar_filmes():
    """Placeholder para filmes - sera implementado depois."""
    dialog = xbmcgui.Dialog()
    dialog.ok(ADDON_NAME, "Secao de filmes em desenvolvimento.\nEm breve estara disponivel!")


def listar_series():
    """Placeholder para series - sera implementado depois."""
    dialog = xbmcgui.Dialog()
    dialog.ok(ADDON_NAME, "Secao de series em desenvolvimento.\nEm breve estara disponivel!")


# ============================================================
# MENU PRINCIPAL
# ============================================================

def menu_principal():
    usuario = get_user_name()
    add_item("TV AO VIVO", "tv_ao_vivo", is_folder=True, plot="Acesse os canais de TV ao vivo")
    add_item("FILMES", "filmes", is_folder=True, plot="Biblioteca de filmes (em desenvolvimento)")
    add_item("SERIES", "series", is_folder=True, plot="Biblioteca de series (em desenvolvimento)")
    add_item("TROCAR SERVIDOR", "trocar_servidor", is_folder=False, plot="Selecione outro servidor")
    add_item("CONTROLE PARENTAL", "controle_parental", is_folder=False, plot="Configure PIN de controle parental")
    add_item("CONFIGURACOES", "configuracoes", is_folder=False, plot="Configuracoes do addon")
    add_item("SAIR (Logout)", "logout", is_folder=False, plot="Desconectar da conta")
    xbmcplugin.endOfDirectory(HANDLE)


def router(paramstring):
    """Router de acoes."""
    params = dict(parse_qsl(paramstring))
    action = params.get('action', '')
    
    if not action:
        if is_logged_in():
            menu_principal()
        else:
            if do_login():
                menu_principal()
    elif action == 'tv_ao_vivo':
        listar_canais_tv()
    elif action == 'filmes':
        listar_filmes()
    elif action == 'series':
        listar_series()
    elif action == 'trocar_servidor':
        show_servers()
    elif action == 'controle_parental':
        show_parental_menu()
    elif action == 'configuracoes':
        xbmc.executebuiltin('Addon.OpenSettings({0})'.format(ADDON_ID))
    elif action == 'logout':
        do_logout()


if __name__ == '__main__':
    router(sys.argv[2][1:] if len(sys.argv) > 2 else '')
