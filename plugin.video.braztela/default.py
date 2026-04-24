# -*- coding: utf-8 -*-
"""
BRAZTELA v2.0.1 - Addon IPTV com gerenciamento pelo GitHub
Corrigido para Kodi 21.x (xbmcvfs.translatePath)
"""

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import urllib.request
import json
import os
import time

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
addon_path = addon.getAddonInfo('path')
addon_data_path = xbmcvfs.translatePath('special://profile/addon_data/{0}'.format(addon_id))
cache_dir = os.path.join(addon_data_path, 'cache')

if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

GITHUB_RAW = 'https://raw.githubusercontent.com/brazalvesjr/braztela/main'
SERVIDORES_URL = '{0}/servidores_ativos.json'.format(GITHUB_RAW)
CLIENTES_URL = '{0}/clientes.json'.format(GITHUB_RAW)

def log_debug(msg):
    """Log para debug"""
    xbmc.log('[{0}] {1}'.format(addon_id, msg), xbmc.LOGINFO)

def download_json(url, timeout=10):
    """Baixar JSON do GitHub"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read().decode('utf-8')
            return json.loads(data)
    except Exception as e:
        log_debug('Erro ao baixar {0}: {1}'.format(url, str(e)))
        return None

def validar_cliente(codigo, senha):
    """Validar credenciais do cliente"""
    clientes_data = download_json(CLIENTES_URL)
    if not clientes_data:
        xbmcgui.Dialog().notification('Erro', 'Nao foi possivel validar cliente', xbmcgui.NOTIFICATION_ERROR)
        return False
    
    for cliente in clientes_data.get('clientes', []):
        if cliente.get('codigo') == codigo and cliente.get('senha') == senha:
            if cliente.get('ativo', True):
                return True
            else:
                xbmcgui.Dialog().notification('Bloqueado', 'Cliente bloqueado', xbmcgui.NOTIFICATION_ERROR)
                return False
    
    xbmcgui.Dialog().notification('Erro', 'Codigo ou senha invalidos', xbmcgui.NOTIFICATION_ERROR)
    return False

def obter_servidores():
    """Obter lista de servidores ativos"""
    servidores_data = download_json(SERVIDORES_URL)
    if not servidores_data:
        xbmcgui.Dialog().notification('Erro', 'Nao foi possivel obter servidores', xbmcgui.NOTIFICATION_ERROR)
        return []
    
    servidores_ativos = []
    for servidor in servidores_data.get('servidores', []):
        if servidor.get('ativo', True):
            servidores_ativos.append(servidor)
    
    return servidores_ativos

def menu_principal():
    """Menu principal do addon"""
    xbmcplugin.setPluginCategory(int(sys.argv[1]), 'BRAZTELA')
    
    item = xbmcgui.ListItem('TV AO VIVO')
    item.setArt({'icon': 'DefaultFolder.png'})
    url = sys.argv[0] + '?action=tv_ao_vivo'
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, isFolder=True)
    
    item = xbmcgui.ListItem('FILMES')
    item.setArt({'icon': 'DefaultFolder.png'})
    url = sys.argv[0] + '?action=filmes'
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, isFolder=True)
    
    item = xbmcgui.ListItem('SERIES')
    item.setArt({'icon': 'DefaultFolder.png'})
    url = sys.argv[0] + '?action=series'
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, isFolder=True)
    
    item = xbmcgui.ListItem('TROCAR SERVIDOR')
    item.setArt({'icon': 'DefaultFolder.png'})
    url = sys.argv[0] + '?action=trocar_servidor'
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, isFolder=True)
    
    item = xbmcgui.ListItem('SAIR')
    item.setArt({'icon': 'DefaultFolder.png'})
    url = sys.argv[0] + '?action=sair'
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, isFolder=False)
    
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def tela_login():
    """Tela de login"""
    keyboard = xbmc.Keyboard('', 'Digite seu codigo de cliente:')
    keyboard.doModal()
    if not keyboard.isConfirmed():
        return False
    
    codigo = keyboard.getText()
    if not codigo:
        return False
    
    keyboard = xbmc.Keyboard('', 'Digite sua senha:')
    keyboard.doModal()
    if not keyboard.isConfirmed():
        return False
    
    senha = keyboard.getText()
    if not senha:
        return False
    
    return validar_cliente(codigo, senha)

def main():
    """Funcao principal"""
    import sys
    from urllib.parse import parse_qs, urlparse
    
    # Tela de login
    if not tela_login():
        return
    
    # Parse URL
    url = urlparse(sys.argv[0])
    params = parse_qs(url.query)
    action = params.get('action', [''])[0]
    
    if action == 'tv_ao_vivo':
        xbmcgui.Dialog().notification('Info', 'TV AO VIVO em desenvolvimento', xbmcgui.NOTIFICATION_INFO)
    elif action == 'filmes':
        xbmcgui.Dialog().notification('Info', 'FILMES em desenvolvimento', xbmcgui.NOTIFICATION_INFO)
    elif action == 'series':
        xbmcgui.Dialog().notification('Info', 'SERIES em desenvolvimento', xbmcgui.NOTIFICATION_INFO)
    elif action == 'trocar_servidor':
        servidores = obter_servidores()
        if servidores:
            nomes = ['Servidor {0}'.format(s.get('id', i)) for i, s in enumerate(servidores)]
            dialog = xbmcgui.Dialog()
            idx = dialog.select('Selecione um servidor', nomes)
            if idx >= 0:
                xbmcgui.Dialog().notification('Sucesso', 'Servidor {0} selecionado'.format(idx + 1), xbmcgui.NOTIFICATION_INFO)
    elif action == 'sair':
        return
    else:
        menu_principal()

if __name__ == '__main__':
    import sys
    main()
