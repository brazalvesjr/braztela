#!/usr/bin/python
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
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
from urllib.parse import urlencode, parse_qsl

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_NAME = "BRAZTELA"
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
PROFILE_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
ICON = os.path.join(ADDON_PATH, 'icon.png')
FANART = os.path.join(ADDON_PATH, 'fanart.jpg')

if not os.path.exists(PROFILE_PATH):
    try:
        os.makedirs(PROFILE_PATH)
    except:
        pass

HANDLE = int(sys.argv[1]) if len(sys.argv) > 1 else -1
BASE_URL = sys.argv[0] if len(sys.argv) > 0 else 'plugin://plugin.video.braztela/'

# CLIENTES
CLIENTES = {
    "TESTE": {"senha": "123456", "nome": "Cliente Teste", "ativo": True},
    "BRAZ": {"senha": "admin2026", "nome": "Braz Junior (Admin)", "ativo": True},
    "CLIENTE001": {"senha": "senha123456", "nome": "Cliente 001", "ativo": True},
    "CLIENTE002": {"senha": "acesso2026", "nome": "Cliente 002", "ativo": True},
    "CLIENTE003": {"senha": "premium789", "nome": "Cliente 003", "ativo": True},
    "CLIENTE004": {"senha": "streaming001", "nome": "Cliente 004", "ativo": True},
    "CLIENTE005": {"senha": "braztela2026", "nome": "Cliente 005", "ativo": True},
    "CLIENTE006": {"senha": "vip123456", "nome": "Cliente 006", "ativo": True},
    "CLIENTE007": {"senha": "premium2026", "nome": "Cliente 007", "ativo": True},
    "CLIENTE008": {"senha": "acesso123", "nome": "Cliente 008", "ativo": True},
    "CLIENTE010": {"senha": "braztv2026", "nome": "Cliente 010", "ativo": True},
}

# SERVIDORES
SERVIDORES = []
for i in range(1, 21):
    SERVIDORES.append({
        "id": i,
        "nome": "Servidor #" + str(i),
        "dns": "http://servidor" + str(i) + ".example.com:8080",
        "ativo": (i <= 8),
    })


def log(msg):
    xbmc.log("[BRAZTELA] " + str(msg), xbmc.LOGINFO)


def build_url(action, **kwargs):
    params = {'action': action}
    params.update(kwargs)
    return BASE_URL + '?' + urlencode(params)


def add_item(label, action, is_folder=True, plot="", **kwargs):
    li = xbmcgui.ListItem(label=label)
    li.setArt({'icon': ICON, 'thumb': ICON, 'fanart': FANART})
    if plot:
        try:
            li.getVideoInfoTag().setPlot(plot)
        except:
            pass
    url = build_url(action, **kwargs)
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=li, isFolder=is_folder)


# AUTENTICACAO
def auth_file_path():
    return os.path.join(PROFILE_PATH, 'auth.json')


def is_logged_in():
    f = auth_file_path()
    if os.path.exists(f):
        try:
            with open(f, 'r') as fh:
                data = json.load(fh)
            cod = data.get('codigo', '')
            if cod in CLIENTES and CLIENTES[cod].get('ativo', False):
                return True
        except:
            pass
    return False


def get_user_name():
    f = auth_file_path()
    if os.path.exists(f):
        try:
            with open(f, 'r') as fh:
                data = json.load(fh)
            return data.get('nome', 'Usuario')
        except:
            pass
    return 'Usuario'


def do_login():
    dialog = xbmcgui.Dialog()
    dialog.ok(ADDON_NAME, "Bem-vindo ao BRAZTELA!\n\nInforme seu Codigo de Cliente e Senha de Acesso.\n(Fornecidos por Braz Junior)")
    
    codigo = dialog.input("Codigo do Cliente", type=xbmcgui.INPUT_ALPHANUMERIC)
    if not codigo:
        return False
    codigo = codigo.upper().strip()
    
    senha = dialog.input("Senha de Acesso", type=xbmcgui.INPUT_ALPHANUMERIC, option=xbmcgui.ALPHANUM_HIDE_INPUT)
    if not senha:
        return False
    
    if codigo not in CLIENTES:
        dialog.ok(ADDON_NAME, "Codigo invalido!")
        return False
    
    cliente = CLIENTES[codigo]
    if not cliente.get('ativo', False):
        dialog.ok(ADDON_NAME, "Cliente bloqueado!\n\nContate Braz Junior.")
        return False
    
    if cliente['senha'] != senha:
        dialog.ok(ADDON_NAME, "Senha incorreta!")
        return False
    
    try:
        with open(auth_file_path(), 'w') as fh:
            json.dump({'codigo': codigo, 'nome': cliente['nome']}, fh)
    except:
        pass
    
    dialog.notification(ADDON_NAME, "Bem-vindo, " + cliente['nome'] + "!", ICON, 3000)
    return True


def do_logout():
    f = auth_file_path()
    if os.path.exists(f):
        try:
            os.remove(f)
        except:
            pass
    xbmcgui.Dialog().notification(ADDON_NAME, "Sessao encerrada", ICON, 2000)


# CONTROLE PARENTAL
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
        except:
            pass
    
    if pin_atual is None:
        novo = dialog.input("Crie um PIN de 4 digitos", type=xbmcgui.INPUT_NUMERIC)
        if novo and len(novo) >= 4:
            try:
                with open(pf, 'w') as fh:
                    json.dump({'pin': novo}, fh)
                dialog.ok(ADDON_NAME, "PIN parental criado!")
            except:
                dialog.ok(ADDON_NAME, "Erro ao salvar PIN")
        return
    
    opcoes = ["Alterar PIN", "Desativar Controle Parental", "Cancelar"]
    escolha = dialog.select("Controle Parental", opcoes)
    if escolha == 0:
        check = dialog.input("PIN atual", type=xbmcgui.INPUT_NUMERIC)
        if check == pin_atual:
            novo = dialog.input("Novo PIN (4 digitos)", type=xbmcgui.INPUT_NUMERIC)
            if novo and len(novo) >= 4:
                with open(pf, 'w') as fh:
                    json.dump({'pin': novo}, fh)
                dialog.ok(ADDON_NAME, "PIN alterado!")
        else:
            dialog.ok(ADDON_NAME, "PIN incorreto!")
    elif escolha == 1:
        check = dialog.input("PIN para desativar", type=xbmcgui.INPUT_NUMERIC)
        if check == pin_atual:
            os.remove(pf)
            dialog.ok(ADDON_NAME, "Controle parental desativado.")


# SERVIDORES
def get_current_server():
    return ADDON.getSetting('servidor_atual') or '1'


def show_servers():
    dialog = xbmcgui.Dialog()
    ativos = [s for s in SERVIDORES if s.get('ativo', False)]
    if not ativos:
        dialog.ok(ADDON_NAME, "Nenhum servidor disponivel.")
        return
    nomes = []
    atual = get_current_server()
    for s in ativos:
        prefixo = "[ATIVO] " if str(s['id']) == atual else ""
        nomes.append(prefixo + s['nome'])
    escolha = dialog.select("Selecione um Servidor", nomes)
    if escolha >= 0:
        s = ativos[escolha]
        ADDON.setSetting('servidor_atual', str(s['id']))
        dialog.notification(ADDON_NAME, "Servidor: " + s['nome'], ICON, 3000)


# MENUS
def show_main_menu():
    user = get_user_name()
    xbmcplugin.setPluginCategory(HANDLE, "BRAZTELA - " + user)
    xbmcplugin.setContent(HANDLE, 'videos')
    
    add_item("[B][COLOR red]TV AO VIVO[/COLOR][/B]", "tv_live",
             plot="Acesse os canais de TV ao vivo do servidor atual.")
    add_item("[B][COLOR red]FILMES[/COLOR][/B]", "movies",
             plot="Biblioteca completa de filmes com sinopse, capa e metadados.")
    add_item("[B][COLOR red]SERIES[/COLOR][/B]", "series",
             plot="Series com episodios, sinopse e capa.")
    add_item("[B][COLOR yellow]TROCAR SERVIDOR[/COLOR][/B]", "servers",
             plot="Selecione entre os 20 servidores disponiveis.", is_folder=False)
    add_item("[B][COLOR cyan]CONTROLE PARENTAL[/COLOR][/B]", "parental",
             plot="Configure PIN para controle parental.", is_folder=False)
    add_item("[B][COLOR white]CONFIGURACOES[/COLOR][/B]", "settings",
             plot="Configuracoes do addon.", is_folder=False)
    add_item("[COLOR gray]SAIR (Logout)[/COLOR]", "logout",
             plot="Encerrar sessao atual.", is_folder=False)
    
    xbmcplugin.endOfDirectory(HANDLE)


def show_placeholder(title):
    xbmcplugin.setPluginCategory(HANDLE, title)
    xbmcplugin.setContent(HANDLE, 'videos')
    add_item("[I]Aguardando configuracao do servidor...[/I]", "main",
             plot="O administrador esta configurando os servidores. Em breve voce tera acesso ao conteudo.",
             is_folder=False)
    xbmcplugin.endOfDirectory(HANDLE)


def router():
    if not is_logged_in():
        if not do_login():
            xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
            return
    
    params = {}
    if len(sys.argv) > 2 and sys.argv[2]:
        try:
            params = dict(parse_qsl(sys.argv[2][1:]))
        except:
            params = {}
    
    action = params.get('action', 'main')
    log("Acao: " + action)
    
    if action == 'main':
        show_main_menu()
    elif action == 'tv_live':
        show_placeholder("TV AO VIVO")
    elif action == 'movies':
        show_placeholder("FILMES")
    elif action == 'series':
        show_placeholder("SERIES")
    elif action == 'servers':
        show_servers()
    elif action == 'parental':
        show_parental_menu()
    elif action == 'settings':
        ADDON.openSettings()
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
            xbmcgui.Dialog().notification(ADDON_NAME, "Erro: " + str(e)[:50], xbmcgui.NOTIFICATION_ERROR, 5000)
        except:
            pass
