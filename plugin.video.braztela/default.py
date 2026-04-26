# -*- coding: utf-8 -*-
"""
BRAZTELA - Addon Premium para Kodi
Desenvolvido por Braz Junior
Versao 1.4 - Categorias, Busca e Interface Melhorada
"""
import sys
import os
import json

try:
    import xbmc
    import xbmcaddon
    import xbmcgui
    import xbmcplugin
    import xbmcvfs
except ImportError:
    sys.exit(0)

try:
    from urllib.parse import urlencode, parse_qsl
    from urllib.request import Request, urlopen
except ImportError:
    from urllib import urlencode
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
CANAIS_URL = GITHUB_RAW + "/canais.json"
FILMES_URL = GITHUB_RAW + "/filmes.json"
SERIES_URL = GITHUB_RAW + "/series.json"

# Categorias de SÉRIES (conforme solicitado)
CATEGORIAS_SERIES = [
    "TURCAS",
    "NETFLIX",
    "PRIME VÍDEO",
    "NOVELAS",
    "AMC",
    "APPLE",
    "BRASIL PARALELO",
    "DISCOVERY PLUS",
    "DISNEY PLUS"
]


def log(msg):
    try:
        xbmc.log("[BRAZTELA] " + str(msg), xbmc.LOGINFO)
    except Exception:
        pass


def http_get(url, timeout=10):
    """Baixa JSON com timeout."""
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    try:
        req = Request(url, headers={'User-Agent': ua})
        resp = urlopen(req, timeout=timeout)
        data = resp.read()
        if isinstance(data, bytes):
            try:
                data = data.decode('utf-8')
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


def add_playable(label, stream_url, logo="", plot=""):
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
        if plot:
            info_tag.setPlot(plot)
    except Exception:
        try:
            li.setInfo('video', {'title': label, 'plot': plot or ''})
        except Exception:
            pass
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=stream_url, listitem=li, isFolder=False)


def get_input(heading, hidden=False):
    """Teclado Kodi."""
    try:
        kb = xbmc.Keyboard('', heading, hidden)
        kb.doModal()
        if not kb.isConfirmed():
            return None
        return kb.getText().strip() if kb.getText() else None
    except Exception:
        return None


# ============================================================
# AUTENTICACAO
# ============================================================

def carregar_clientes():
    """Baixa clientes.json do GitHub."""
    try:
        data = http_get(CLIENTES_URL, timeout=10)
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
    except Exception:
        pass

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
# CATEGORIAS - TV AO VIVO
# ============================================================

def listar_categorias_canais():
    """Lista categorias de canais para o usuário adicionar conteúdo no GitHub."""
    dialog = xbmcgui.Dialog()
    data = http_get(CANAIS_URL, timeout=10)
    
    if not data:
        dialog.ok(ADDON_NAME, "Erro ao carregar canais.\nVerifique sua conexao.")
        return
    
    try:
        obj = json.loads(data)
        canais = obj.get('canais', [])
    except Exception:
        dialog.ok(ADDON_NAME, "Erro ao processar lista de canais.")
        return
    
    # Extrair categorias únicas
    categorias = set()
    for canal in canais:
        cat = canal.get('categoria', 'Sem categoria')
        if cat:
            categorias.add(cat)
    
    if not categorias:
        dialog.ok(ADDON_NAME, "Nenhuma categoria disponivel.")
        return
    
    # Mostrar categorias
    for categoria in sorted(categorias):
        add_item(categoria, "canais_categoria", is_folder=True, 
                plot="Canais de " + categoria, categoria=categoria)
    
    xbmcplugin.endOfDirectory(HANDLE)


def listar_canais_por_categoria(categoria):
    """Lista canais de uma categoria específica."""
    dialog = xbmcgui.Dialog()
    data = http_get(CANAIS_URL, timeout=10)
    
    if not data:
        dialog.ok(ADDON_NAME, "Erro ao carregar canais.\nVerifique sua conexao.")
        return
    
    try:
        obj = json.loads(data)
        canais = obj.get('canais', [])
    except Exception:
        dialog.ok(ADDON_NAME, "Erro ao processar lista de canais.")
        return
    
    # Filtrar por categoria
    canais_filtrados = [c for c in canais if c.get('categoria') == categoria and c.get('ativo', False)]
    
    if not canais_filtrados:
        dialog.ok(ADDON_NAME, "Nenhum canal disponivel nesta categoria.")
        return
    
    for canal in canais_filtrados:
        add_playable(canal.get('nome', 'Canal'), canal.get('url', ''), canal.get('logo', ''))
    
    xbmcplugin.endOfDirectory(HANDLE)


# ============================================================
# CATEGORIAS - FILMES
# ============================================================

def listar_categorias_filmes():
    """Lista categorias de filmes."""
    dialog = xbmcgui.Dialog()
    data = http_get(FILMES_URL, timeout=10)
    
    if not data:
        dialog.ok(ADDON_NAME, "Erro ao carregar filmes.\nVerifique sua conexao.")
        return
    
    try:
        obj = json.loads(data)
        filmes = obj.get('filmes', [])
    except Exception:
        dialog.ok(ADDON_NAME, "Erro ao processar lista de filmes.")
        return
    
    # Extrair categorias únicas
    categorias = set()
    for filme in filmes:
        cat = filme.get('genero', 'Sem categoria')
        if cat:
            categorias.add(cat)
    
    if not categorias:
        dialog.ok(ADDON_NAME, "Nenhuma categoria disponivel.")
        return
    
    # Mostrar categorias
    for categoria in sorted(categorias):
        add_item(categoria, "filmes_categoria", is_folder=True, 
                plot="Filmes de " + categoria, categoria=categoria)
    
    xbmcplugin.endOfDirectory(HANDLE)


def listar_filmes_por_categoria(categoria):
    """Lista filmes de uma categoria específica."""
    dialog = xbmcgui.Dialog()
    data = http_get(FILMES_URL, timeout=10)
    
    if not data:
        dialog.ok(ADDON_NAME, "Erro ao carregar filmes.\nVerifique sua conexao.")
        return
    
    try:
        obj = json.loads(data)
        filmes = obj.get('filmes', [])
    except Exception:
        dialog.ok(ADDON_NAME, "Erro ao processar lista de filmes.")
        return
    
    # Filtrar por categoria
    filmes_filtrados = [f for f in filmes if f.get('genero') == categoria and f.get('ativo', False)]
    
    if not filmes_filtrados:
        dialog.ok(ADDON_NAME, "Nenhum filme disponivel nesta categoria.")
        return
    
    for filme in filmes_filtrados:
        add_playable(filme.get('nome', 'Filme'), filme.get('url', ''), 
                    filme.get('logo', ''), filme.get('sinopse', ''))
    
    xbmcplugin.endOfDirectory(HANDLE)


# ============================================================
# CATEGORIAS - SÉRIES
# ============================================================

def listar_categorias_series():
    """Lista categorias de séries."""
    # Mostrar categorias pré-definidas
    for categoria in CATEGORIAS_SERIES:
        add_item(categoria, "series_categoria", is_folder=True, 
                plot="Series de " + categoria, categoria=categoria)
    
    xbmcplugin.endOfDirectory(HANDLE)


def listar_series_por_categoria(categoria):
    """Lista séries de uma categoria específica."""
    dialog = xbmcgui.Dialog()
    data = http_get(SERIES_URL, timeout=10)
    
    if not data:
        dialog.ok(ADDON_NAME, "Erro ao carregar series.\nVerifique sua conexao.")
        return
    
    try:
        obj = json.loads(data)
        series = obj.get('series', [])
    except Exception:
        dialog.ok(ADDON_NAME, "Erro ao processar lista de series.")
        return
    
    # Filtrar por categoria
    series_filtradas = [s for s in series if s.get('categoria') == categoria and s.get('ativo', False)]
    
    if not series_filtradas:
        dialog.ok(ADDON_NAME, "Nenhuma serie disponivel nesta categoria.")
        return
    
    for serie in series_filtradas:
        add_playable(serie.get('nome', 'Serie'), serie.get('url', ''), 
                    serie.get('logo', ''), serie.get('sinopse', ''))
    
    xbmcplugin.endOfDirectory(HANDLE)


# ============================================================
# BUSCA
# ============================================================

def buscar_conteudo():
    """Busca filmes e séries."""
    termo = get_input("Digite o nome do filme ou serie", hidden=False)
    if not termo:
        return
    
    termo = termo.lower().strip()
    dialog = xbmcgui.Dialog()
    
    # Buscar filmes
    data_filmes = http_get(FILMES_URL, timeout=10)
    filmes_encontrados = []
    if data_filmes:
        try:
            obj = json.loads(data_filmes)
            filmes = obj.get('filmes', [])
            filmes_encontrados = [f for f in filmes if termo in f.get('nome', '').lower() and f.get('ativo', False)]
        except Exception:
            pass
    
    # Buscar séries
    data_series = http_get(SERIES_URL, timeout=10)
    series_encontradas = []
    if data_series:
        try:
            obj = json.loads(data_series)
            series = obj.get('series', [])
            series_encontradas = [s for s in series if termo in s.get('nome', '').lower() and s.get('ativo', False)]
        except Exception:
            pass
    
    if not filmes_encontrados and not series_encontradas:
        dialog.ok(ADDON_NAME, "Nenhum resultado encontrado para: " + termo)
        return
    
    # Mostrar filmes
    for filme in filmes_encontrados:
        add_playable("[FILME] " + filme.get('nome', 'Filme'), filme.get('url', ''), 
                    filme.get('logo', ''), filme.get('sinopse', ''))
    
    # Mostrar séries
    for serie in series_encontradas:
        add_playable("[SERIE] " + serie.get('nome', 'Serie'), serie.get('url', ''), 
                    serie.get('logo', ''), serie.get('sinopse', ''))
    
    xbmcplugin.endOfDirectory(HANDLE)


# ============================================================
# MENU PRINCIPAL
# ============================================================

def menu_principal():
    usuario = get_user_name()
    add_item("TV AO VIVO", "tv_ao_vivo", is_folder=True, plot="Acesse os canais de TV ao vivo por categoria")
    add_item("FILMES", "filmes", is_folder=True, plot="Biblioteca de filmes por categoria")
    add_item("SERIES", "series", is_folder=True, plot="Biblioteca de series por categoria")
    add_item("BUSCA", "busca", is_folder=False, plot="Buscar filmes e series")
    add_item("CONTROLE PARENTAL", "controle_parental", is_folder=False, plot="Configure PIN de controle parental")
    add_item("SAIR (Logout)", "logout", is_folder=False, plot="Desconectar da conta")
    xbmcplugin.endOfDirectory(HANDLE)


def router(paramstring):
    """Router de acoes."""
    params = dict(parse_qsl(paramstring))
    action = params.get('action', '')
    categoria = params.get('categoria', '')
    
    if not action:
        if is_logged_in():
            menu_principal()
        else:
            if do_login():
                menu_principal()
    elif action == 'tv_ao_vivo':
        listar_categorias_canais()
    elif action == 'canais_categoria':
        listar_canais_por_categoria(categoria)
    elif action == 'filmes':
        listar_categorias_filmes()
    elif action == 'filmes_categoria':
        listar_filmes_por_categoria(categoria)
    elif action == 'series':
        listar_categorias_series()
    elif action == 'series_categoria':
        listar_series_por_categoria(categoria)
    elif action == 'busca':
        buscar_conteudo()
    elif action == 'controle_parental':
        show_parental_menu()
    elif action == 'logout':
        do_logout()


if __name__ == '__main__':
    router(sys.argv[2][1:] if len(sys.argv) > 2 else '')
