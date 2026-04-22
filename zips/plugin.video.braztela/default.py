#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import xbmcgui
import xbmcplugin
import xbmcaddon

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
handle = int(sys.argv[1])

# Dados dos clientes
CLIENTES = {
    'TESTE': '123456',
    'CLIENTE001': 'senha123456',
    'CLIENTE002': 'acesso2026',
    'CLIENTE003': 'premium789',
    'CLIENTE004': 'streaming001',
    'CLIENTE005': 'braztela2026',
}

def menu_principal():
    """Menu principal do addon"""
    items = [
        ('📺 TV ao Vivo', 'live'),
        ('🎬 Filmes', 'movies'),
        ('📺 Séries', 'series'),
        ('🖥️ Trocar Servidor', 'servers'),
        ('🔒 Controle Parental', 'parental'),
        ('⚙️ Configurações', 'settings'),
    ]
    
    for label, action in items:
        url = f'plugin://{addon_id}/?action={action}'
        item = xbmcgui.ListItem(label)
        xbmcplugin.addDirectoryItem(handle, url, item, True)
    
    xbmcplugin.endOfDirectory(handle)

def autenticar():
    """Autentica o cliente"""
    dialog = xbmcgui.Dialog()
    
    # Pedir código
    codigo = dialog.input('Código do Cliente:')
    if not codigo:
        return False
    
    if codigo not in CLIENTES:
        dialog.notification('Erro', 'Código inválido!', xbmcgui.NOTIFICATION_ERROR)
        return False
    
    # Pedir senha
    senha = dialog.input('Senha:', option=xbmcgui.INPUT_PASSWORD)
    if not senha:
        return False
    
    if CLIENTES[codigo] != senha:
        dialog.notification('Erro', 'Senha incorreta!', xbmcgui.NOTIFICATION_ERROR)
        return False
    
    dialog.notification('Sucesso', f'Bem-vindo {codigo}!', xbmcgui.NOTIFICATION_INFO)
    addon.setSetting('cliente', codigo)
    return True

def tv_ao_vivo():
    """Menu de TV ao Vivo"""
    item = xbmcgui.ListItem('📡 TV ao Vivo - Em desenvolvimento')
    xbmcplugin.addDirectoryItem(handle, '', item, False)
    xbmcplugin.endOfDirectory(handle)

def filmes():
    """Menu de Filmes"""
    item = xbmcgui.ListItem('🎬 Filmes - Em desenvolvimento')
    xbmcplugin.addDirectoryItem(handle, '', item, False)
    xbmcplugin.endOfDirectory(handle)

def series():
    """Menu de Séries"""
    item = xbmcgui.ListItem('📺 Séries - Em desenvolvimento')
    xbmcplugin.addDirectoryItem(handle, '', item, False)
    xbmcplugin.endOfDirectory(handle)

def servidores():
    """Menu de Servidores"""
    servidores_list = [
        ('🔴 Premium HD 1', 'Servidor Premium'),
        ('🔴 Premium HD 2', 'Servidor Premium - Backup'),
        ('🟡 4K Ultra 1', 'Servidor 4K'),
        ('🟡 4K Ultra 2', 'Servidor 4K - Backup'),
        ('🟢 Streaming 1', 'Servidor Streaming'),
        ('🟢 Streaming 2', 'Servidor Streaming - Backup'),
        ('🔵 Internacional 1', 'Servidor Internacional'),
        ('🔵 Internacional 2', 'Servidor Internacional - Backup'),
        ('🟣 Backup 1', 'Servidor Backup'),
        ('🟣 Backup 2', 'Servidor Backup'),
        ('⚪ Reserva 1', 'Servidor Reserva'),
        ('⚪ Reserva 2', 'Servidor Reserva'),
        ('🟠 Teste 1', 'Servidor Teste'),
        ('🟠 Teste 2', 'Servidor Teste'),
        ('🔶 Espelho 1', 'Servidor Espelho'),
        ('🔶 Espelho 2', 'Servidor Espelho'),
        ('🟥 Emergência 1', 'Servidor Emergência'),
        ('🟥 Emergência 2', 'Servidor Emergência'),
        ('⬛ Secundário 1', 'Servidor Secundário'),
        ('⬛ Secundário 2', 'Servidor Secundário'),
    ]
    
    for nome, desc in servidores_list:
        item = xbmcgui.ListItem(nome)
        item.setInfo('video', {'plot': desc})
        xbmcplugin.addDirectoryItem(handle, '', item, False)
    
    xbmcplugin.endOfDirectory(handle)

def controle_parental():
    """Menu de Controle Parental"""
    item = xbmcgui.ListItem('🔒 Controle Parental - Ativo')
    xbmcplugin.addDirectoryItem(handle, '', item, False)
    xbmcplugin.endOfDirectory(handle)

def configuracoes():
    """Abre configurações"""
    addon.openSettings()

# Main
if __name__ == '__main__':
    try:
        params = {}
        if len(sys.argv) > 2:
            params_str = sys.argv[2].lstrip('?')
            for param in params_str.split('&'):
                if '=' in param:
                    k, v = param.split('=', 1)
                    params[k] = v
        
        action = params.get('action', 'main')
        
        # Verificar autenticação
        cliente = addon.getSetting('cliente')
        if action not in ['main', 'settings'] and not cliente:
            if not autenticar():
                menu_principal()
                sys.exit(0)
        
        # Roteamento
        if action == 'main':
            menu_principal()
        elif action == 'live':
            tv_ao_vivo()
        elif action == 'movies':
            filmes()
        elif action == 'series':
            series()
        elif action == 'servers':
            servidores()
        elif action == 'parental':
            controle_parental()
        elif action == 'settings':
            configuracoes()
        else:
            menu_principal()
    except Exception as e:
        xbmcgui.Dialog().notification('Erro', str(e), xbmcgui.NOTIFICATION_ERROR)
