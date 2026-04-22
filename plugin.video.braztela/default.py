# -*- coding: utf-8 -*-
"""
BRAZTELA - Addon Premium para Kodi
Desenvolvido por Braz Junior
Versao 1.0.0
"""
import sys
import os
import json
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs

try:
    from urllib.parse import urlencode, parse_qsl, quote, unquote
except ImportError:
    from urllib import urlencode, quote, unquote
    from urlparse import parse_qsl

# ================================================================
# CONFIGURACOES
# ================================================================
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
PROFILE_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
ICON = os.path.join(ADDON_PATH, 'icon.png')
FANART = os.path.join(ADDON_PATH, 'fanart.jpg')

if not os.path.exists(PROFILE_PATH):
    os.makedirs(PROFILE_PATH)

HANDLE = int(sys.argv[1]) if len(sys.argv) > 1 else -1
BASE_URL = sys.argv[0] if len(sys.argv) > 0 else 'plugin://plugin.video.braztela/'

# ================================================================
# DADOS EMBUTIDOS - SENHAS DOS CLIENTES
# ================================================================
CLIENTES = {
    "TESTE": {"senha": "123456", "nome": "Cliente Teste", "ativo": True, "validade": "2027-12-31"},
    "BRAZ": {"senha": "admin2026", "nome": "Braz Junior", "ativo": True, "validade": "2099-12-31"},
    "CLIENTE001": {"senha": "senha123456", "nome": "Joao Silva", "ativo": True, "validade": "2026-12-31"},
    "CLIENTE002": {"senha": "acesso2026", "nome": "Maria Santos", "ativo": True, "validade": "2026-12-31"},
    "CLIENTE003": {"senha": "premium789", "nome": "Carlos Oliveira", "ativo": True, "validade": "2026-12-31"},
    "CLIENTE004": {"senha": "streaming001", "nome": "Ana Costa", "ativo": True, "validade": "2026-12-31"},
    "CLIENTE005": {"senha": "braztela2026", "nome": "Pedro Ferreira", "ativo": True, "validade": "2026-12-31"},
    "CLIENTE006": {"senha": "vip123456", "nome": "Fernanda Gomes", "ativo": True, "validade": "2026-12-31"},
    "CLIENTE007": {"senha": "premium2026", "nome": "Roberto Alves", "ativo": True, "validade": "2026-12-31"},
    "CLIENTE008": {"senha": "acesso123", "nome": "Juliana Rocha", "ativo": True, "validade": "2026-12-31"},
    "CLIENTE009": {"senha": "streaming789", "nome": "Lucas Martins", "ativo": False, "validade": "2026-06-30"},
    "CLIENTE010": {"senha": "braztv2026", "nome": "Beatriz Lima", "ativo": True, "validade": "2026-12-31"},
}

# ================================================================
# DADOS EMBUTIDOS - SERVIDORES (20 SLOTS)
# ================================================================
SERVIDORES = [
    {"id": 1, "nome": "Premium HD #1", "dns": "http://servidor1.example.com:8080", "ativo": True},
    {"id": 2, "nome": "Premium HD #2", "dns": "http://servidor2.example.com:8080", "ativo": True},
    {"id": 3, "nome": "Premium 4K #1", "dns": "http://servidor3.example.com:8080", "ativo": True},
    {"id": 4, "nome": "Premium 4K #2", "dns": "http://servidor4.example.com:8080", "ativo": True},
    {"id": 5, "nome": "Backup #1", "dns": "http://servidor5.example.com:8080", "ativo": True},
    {"id": 6, "nome": "Backup #2", "dns": "http://servidor6.example.com:8080", "ativo": True},
    {"id": 7, "nome": "Backup #3", "dns": "http://servidor7.example.com:8080", "ativo": True},
    {"id": 8, "nome": "Backup #4", "dns": "http://servidor8.example.com:8080", "ativo": True},
    {"id": 9, "nome": "Reserva #1", "dns": "http://servidor9.example.com:8080", "ativo": False},
    {"id": 10, "nome": "Reserva #2", "dns": "http://servidor10.example.com:8080", "ativo": False},
    {"id": 11, "nome": "Servidor #11", "dns": "http://servidor11.example.com:8080", "ativo": False},
    {"id": 12, "nome": "Servidor #12", "dns": "http://servidor12.example.com:8080", "ativo": False},
    {"id": 13, "nome": "Servidor #13", "dns": "http://servidor13.example.com:8080", "ativo": False},
    {"id": 14, "nome": "Servidor #14", "dns": "http://servidor14.example.com:8080", "ativo": False},
    {"id": 15, "nome": "Servidor #15", "dns": "http://servidor15.example.com:8080", "ativo": False},
    {"id": 16, "nome": "Servidor #16", "dns": "http://servidor16.example.com:8080", "ativo": False},
    {"id": 17, "nome": "Servidor #17", "dns": "http://servidor17.example.com:8080", "ativo": False},
    {"id": 18, "nome": "Servidor #18", "dns": "http://servidor18.example.com:8080", "ativo": False},
    {"id": 19, "nome": "Servidor #19", "dns": "http://servidor19.example.com:8080", "ativo": False},
    {"id": 20, "nome": "Servidor #20", "dns": "http://servidor20.example.com:8080", "ativo": False},
]

# ================================================================
# UTILITARIOS
# ================================================================
def log(msg):
    """Log no Kodi"""
    xbmc.log("[BRAZTELA] " + str(msg), xbmc.LOGINFO)

def notify(title, msg, icon=None, time=3000):
    """Notificacao na tela"""
    if icon is None:
        icon = ICON
    xbmcgui.Dialog().notification(title, msg, icon, time)

def build_url(action, **kwargs):
    """Construir URL para navegacao interna"""
    params = {'action': action}
    params.update(kwargs)
    return BASE_URL + '?' + urlencode(params)

def add_dir(label, action, icon=None, fanart=None, info=None, is_folder=True, **kwargs):
    """Adicionar item ao diretorio"""
    list_item = xbmcgui.ListItem(label=label)
    
    if icon is None:
        icon = ICON
    if fanart is None:
        fanart = FANART
    
    list_item.setArt({
        'icon': icon,
        'thumb': icon,
        'fanart': fanart,
        'poster': icon
    })
    
    if info:
        try:
            video_info = list_item.getVideoInfoTag()
            if 'plot' in info:
                video_info.setPlot(info['plot'])
            if 'title' in info:
                video_info.setTitle(info['title'])
            if 'year' in info:
                video_info.setYear(info['year'])
        except:
            pass
    
    url = build_url(action, **kwargs)
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=list_item, isFolder=is_folder)

# ================================================================
# AUTENTICACAO
# ================================================================
def get_auth_file():
    """Caminho do arquivo de autenticacao salva"""
    return os.path.join(PROFILE_PATH, 'auth.json')

def is_authenticated():
    """Verifica se ja esta autenticado"""
    auth_file = get_auth_file()
    if os.path.exists(auth_file):
        try:
            with open(auth_file, 'r') as f:
                data = json.load(f)
            codigo = data.get('codigo', '')
            if codigo in CLIENTES and CLIENTES[codigo]['ativo']:
                return True
        except:
            pass
    return False

def save_auth(codigo, nome):
    """Salvar autenticacao"""
    auth_file = get_auth_file()
    try:
        with open(auth_file, 'w') as f:
            json.dump({'codigo': codigo, 'nome': nome}, f)
        return True
    except:
        return False

def get_current_user():
    """Obter usuario atual"""
    auth_file = get_auth_file()
    if os.path.exists(auth_file):
        try:
            with open(auth_file, 'r') as f:
                data = json.load(f)
            return data.get('nome', 'Usuario')
        except:
            pass
    return 'Usuario'

def do_login():
    """Realizar login"""
    dialog = xbmcgui.Dialog()
    
    dialog.ok(
        ADDON_NAME,
        "Bem-vindo ao BRAZTELA!\n\nInforme seu Codigo de Cliente e Senha de Acesso.\n(Fornecidos por Braz Junior)"
    )
    
    codigo = dialog.input("Codigo do Cliente", type=xbmcgui.INPUT_ALPHANUMERIC)
    if not codigo:
        return False
    codigo = codigo.upper().strip()
    
    senha = dialog.input("Senha de Acesso", type=xbmcgui.INPUT_ALPHANUMERIC, option=xbmcgui.ALPHANUM_HIDE_INPUT)
    if not senha:
        return False
    
    if codigo not in CLIENTES:
        dialog.ok(ADDON_NAME, "Codigo de cliente invalido!\n\nVerifique e tente novamente.")
        return False
    
    cliente = CLIENTES[codigo]
    
    if not cliente['ativo']:
        dialog.ok(ADDON_NAME, "Cliente bloqueado!\n\nEntre em contato com Braz Junior.")
        return False
    
    if cliente['senha'] != senha:
        dialog.ok(ADDON_NAME, "Senha incorreta!\n\nVerifique e tente novamente.")
        return False
    
    save_auth(codigo, cliente['nome'])
    notify(ADDON_NAME, "Bem-vindo, " + cliente['nome'] + "!", time=3000)
    return True

def do_logout():
    """Sair (logout)"""
    auth_file = get_auth_file()
    if os.path.exists(auth_file):
        os.remove(auth_file)
    notify(ADDON_NAME, "Sessao encerrada", time=2000)

# ================================================================
# CONTROLE PARENTAL
# ================================================================
def get_parental_file():
    return os.path.join(PROFILE_PATH, 'parental.json')

def get_parental_pin():
    """Obter PIN parental salvo"""
    pf = get_parental_file()
    if os.path.exists(pf):
        try:
            with open(pf, 'r') as f:
                data = json.load(f)
            return data.get('pin', None)
        except:
            pass
    return None

def set_parental_pin(pin):
    """Salvar PIN parental"""
    pf = get_parental_file()
    try:
        with open(pf, 'w') as f:
            json.dump({'pin': pin, 'enabled': True}, f)
        return True
    except:
        return False

def show_parental_menu():
    """Menu de controle parental"""
    dialog = xbmcgui.Dialog()
    pin_atual = get_parental_pin()
    
    if pin_atual is None:
        # Configurar PIN pela primeira vez
        novo_pin = dialog.input("Crie um PIN de 4 digitos", type=xbmcgui.INPUT_NUMERIC)
        if novo_pin and len(novo_pin) >= 4:
            set_parental_pin(novo_pin)
            dialog.ok(ADDON_NAME, "PIN parental criado com sucesso!")
        else:
            dialog.ok(ADDON_NAME, "PIN deve ter pelo menos 4 digitos.")
    else:
        opcoes = ["Alterar PIN", "Desativar Controle Parental", "Cancelar"]
        escolha = dialog.select("Controle Parental", opcoes)
        
        if escolha == 0:
            pin_check = dialog.input("Digite o PIN atual", type=xbmcgui.INPUT_NUMERIC)
            if pin_check == pin_atual:
                novo = dialog.input("Novo PIN (4 digitos)", type=xbmcgui.INPUT_NUMERIC)
                if novo and len(novo) >= 4:
                    set_parental_pin(novo)
                    dialog.ok(ADDON_NAME, "PIN alterado com sucesso!")
            else:
                dialog.ok(ADDON_NAME, "PIN incorreto!")
        elif escolha == 1:
            pin_check = dialog.input("Digite o PIN para desativar", type=xbmcgui.INPUT_NUMERIC)
            if pin_check == pin_atual:
                pf = get_parental_file()
                if os.path.exists(pf):
                    os.remove(pf)
                dialog.ok(ADDON_NAME, "Controle parental desativado.")

# ================================================================
# SERVIDORES
# ================================================================
def get_servidor_atual():
    """Obter servidor selecionado"""
    return ADDON.getSetting('servidor_atual') or '1'

def set_servidor_atual(server_id):
    """Definir servidor selecionado"""
    ADDON.setSetting('servidor_atual', str(server_id))

def show_servers():
    """Mostrar lista de servidores ativos"""
    dialog = xbmcgui.Dialog()
    
    # Filtrar apenas servidores ativos
    servidores_ativos = [s for s in SERVIDORES if s['ativo']]
    
    if not servidores_ativos:
        dialog.ok(ADDON_NAME, "Nenhum servidor disponivel no momento.")
        return
    
    nomes = [s['nome'] for s in servidores_ativos]
    atual = get_servidor_atual()
    
    # Marcar o servidor atual
    for i, s in enumerate(servidores_ativos):
        if str(s['id']) == atual:
            nomes[i] = "[ATIVO] " + nomes[i]
    
    escolha = dialog.select("Selecione um Servidor", nomes)
    
    if escolha >= 0:
        servidor = servidores_ativos[escolha]
        set_servidor_atual(servidor['id'])
        notify(ADDON_NAME, "Servidor ativo: " + servidor['nome'], time=3000)

# ================================================================
# MENUS
# ================================================================
def show_main_menu():
    """Menu principal do BRAZTELA"""
    user = get_current_user()
    
    xbmcplugin.setPluginCategory(HANDLE, ADDON_NAME + " - " + user)
    xbmcplugin.setContent(HANDLE, 'videos')
    
    add_dir("[B][COLOR red]TV AO VIVO[/COLOR][/B]", "tv_live", 
            info={'plot': 'Acesse canais de TV ao vivo do servidor selecionado.'})
    
    add_dir("[B][COLOR red]FILMES[/COLOR][/B]", "movies",
            info={'plot': 'Biblioteca completa de filmes com sinopse, capa e metadados.'})
    
    add_dir("[B][COLOR red]SERIES[/COLOR][/B]", "series",
            info={'plot': 'Biblioteca de series com episodios, sinopse e capa.'})
    
    add_dir("[B][COLOR yellow]TROCAR SERVIDOR[/COLOR][/B]", "servers",
            info={'plot': 'Selecione entre os 20 servidores disponiveis.'},
            is_folder=False)
    
    add_dir("[B][COLOR cyan]CONTROLE PARENTAL[/COLOR][/B]", "parental",
            info={'plot': 'Configure PIN para controle parental.'},
            is_folder=False)
    
    add_dir("[B][COLOR white]CONFIGURACOES[/COLOR][/B]", "settings",
            info={'plot': 'Configuracoes do addon BRAZTELA.'},
            is_folder=False)
    
    add_dir("[COLOR gray]SAIR (Logout)[/COLOR]", "logout",
            info={'plot': 'Encerrar sessao atual.'},
            is_folder=False)
    
    xbmcplugin.endOfDirectory(HANDLE)

def show_tv_live():
    """Mostrar TV ao vivo (placeholder)"""
    xbmcplugin.setPluginCategory(HANDLE, "TV ao Vivo")
    xbmcplugin.setContent(HANDLE, 'videos')
    
    servidor = get_servidor_atual()
    add_dir("[I]Conectado ao Servidor #" + str(servidor) + "[/I]", "tv_live",
            info={'plot': 'Aguardando configuracao do DNS do servidor pelo administrador.'},
            is_folder=False)
    
    add_dir("Esportes", "tv_category", category="esportes",
            info={'plot': 'Canais de esportes ao vivo.'})
    add_dir("Filmes", "tv_category", category="filmes",
            info={'plot': 'Canais de filmes 24h.'})
    add_dir("Noticias", "tv_category", category="noticias",
            info={'plot': 'Canais de noticias.'})
    add_dir("Variedades", "tv_category", category="variedades",
            info={'plot': 'Canais de variedades.'})
    add_dir("Infantil", "tv_category", category="infantil",
            info={'plot': 'Canais infantis.'})
    
    xbmcplugin.endOfDirectory(HANDLE)

def show_movies():
    """Mostrar filmes (placeholder)"""
    xbmcplugin.setPluginCategory(HANDLE, "Filmes")
    xbmcplugin.setContent(HANDLE, 'movies')
    
    add_dir("Lancamentos", "movies_cat", category="lancamentos",
            info={'plot': 'Os filmes mais recentes em alta qualidade.'})
    add_dir("Acao", "movies_cat", category="acao",
            info={'plot': 'Filmes de acao e aventura.'})
    add_dir("Comedia", "movies_cat", category="comedia",
            info={'plot': 'Filmes de comedia.'})
    add_dir("Drama", "movies_cat", category="drama",
            info={'plot': 'Filmes de drama.'})
    add_dir("Terror", "movies_cat", category="terror",
            info={'plot': 'Filmes de terror e suspense.'})
    add_dir("Animacao", "movies_cat", category="animacao",
            info={'plot': 'Filmes de animacao para toda a familia.'})
    
    xbmcplugin.endOfDirectory(HANDLE)

def show_series():
    """Mostrar series (placeholder)"""
    xbmcplugin.setPluginCategory(HANDLE, "Series")
    xbmcplugin.setContent(HANDLE, 'tvshows')
    
    add_dir("Series Brasileiras", "series_cat", category="brasileiras",
            info={'plot': 'Series produzidas no Brasil.'})
    add_dir("Series Internacionais", "series_cat", category="internacionais",
            info={'plot': 'Series internacionais dubladas e legendadas.'})
    add_dir("Animes", "series_cat", category="animes",
            info={'plot': 'Animes japoneses.'})
    add_dir("Reality Shows", "series_cat", category="reality",
            info={'plot': 'Reality shows nacionais e internacionais.'})
    
    xbmcplugin.endOfDirectory(HANDLE)

def show_category_placeholder(category):
    """Placeholder para categorias"""
    xbmcplugin.setPluginCategory(HANDLE, category.upper())
    
    item = xbmcgui.ListItem(label="[I]Aguardando configuracao do servidor pelo administrador[/I]")
    item.setArt({'icon': ICON, 'fanart': FANART})
    xbmcplugin.addDirectoryItem(handle=HANDLE, url='', listitem=item, isFolder=False)
    
    xbmcplugin.endOfDirectory(HANDLE)

# ================================================================
# ROTEADOR PRINCIPAL
# ================================================================
def router():
    """Roteador de acoes do plugin"""
    # Verificar autenticacao
    if not is_authenticated():
        if not do_login():
            xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
            return
    
    # Parsear parametros
    params = {}
    if len(sys.argv) > 2 and sys.argv[2]:
        params = dict(parse_qsl(sys.argv[2][1:]))
    
    action = params.get('action', 'main')
    
    log("Acao executada: " + action)
    
    if action == 'main':
        show_main_menu()
    elif action == 'tv_live':
        show_tv_live()
    elif action == 'movies':
        show_movies()
    elif action == 'series':
        show_series()
    elif action == 'servers':
        show_servers()
    elif action == 'parental':
        show_parental_menu()
    elif action == 'settings':
        ADDON.openSettings()
    elif action == 'logout':
        do_logout()
        xbmc.executebuiltin('Container.Refresh')
    elif action == 'tv_category':
        show_category_placeholder(params.get('category', ''))
    elif action == 'movies_cat':
        show_category_placeholder(params.get('category', ''))
    elif action == 'series_cat':
        show_category_placeholder(params.get('category', ''))
    else:
        show_main_menu()

# ================================================================
# EXECUCAO
# ================================================================
if __name__ == '__main__':
    try:
        router()
    except Exception as e:
        log("ERRO: " + str(e))
        xbmcgui.Dialog().notification(ADDON_NAME, "Erro: " + str(e), xbmcgui.NOTIFICATION_ERROR, 5000)
