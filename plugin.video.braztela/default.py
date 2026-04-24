# -*- coding: utf-8 -*-
"""
BRAZTELA v3.0.0 - Addon IPTV Profissional
Desenvolvido por Braz Junior
Compatível com Kodi 21.x
"""

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import urllib.request
import json
import os

# Configurações básicas
addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
addon_path = addon.getAddonInfo('path')
addon_handle = int(xbmcplugin.getSetting(addon_id, 'handle'))

# URLs do GitHub
GITHUB_RAW = 'https://raw.githubusercontent.com/brazalvesjr/braztela/main'
CLIENTES_URL = f'{GITHUB_RAW}/clientes.json'
SERVIDORES_URL = f'{GITHUB_RAW}/servidores_ativos.json'

def log(msg):
    """Log para debug"""
    xbmc.log(f'[BRAZTELA] {msg}', xbmc.LOGINFO)

def show_error(msg):
    """Mostrar erro ao usuário"""
    dialog = xbmcgui.Dialog()
    dialog.notification('BRAZTELA - Erro', msg, xbmcgui.NOTIFICATION_ERROR, 5000)
    log(f'ERRO: {msg}')

def get_json(url):
    """Baixar JSON do GitHub"""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = response.read().decode('utf-8')
            return json.loads(data)
    except Exception as e:
        log(f'Erro ao baixar {url}: {str(e)}')
        return None

def validar_cliente(codigo, senha):
    """Validar credenciais do cliente"""
    clientes_data = get_json(CLIENTES_URL)
    if not clientes_data:
        show_error('Não foi possível conectar ao servidor de autenticação')
        return False
    
    for cliente in clientes_data.get('clientes', []):
        if cliente.get('codigo') == codigo and cliente.get('senha') == senha:
            if cliente.get('ativo', True):
                return True
            else:
                show_error('Cliente bloqueado pelo administrador')
                return False
    
    show_error('Código ou senha incorretos')
    return False

def pedir_credenciais():
    """Pedir código e senha do cliente"""
    keyboard = xbmc.Keyboard('', 'Digite seu código de cliente:')
    keyboard.doModal()
    if not keyboard.isConfirmed():
        return None, None
    codigo = keyboard.getText()
    
    keyboard = xbmc.Keyboard('', 'Digite sua senha:')
    keyboard.doModal()
    if not keyboard.isConfirmed():
        return None, None
    senha = keyboard.getText()
    
    return codigo, senha

def listar_servidores():
    """Listar servidores disponíveis"""
    servidores_data = get_json(SERVIDORES_URL)
    if not servidores_data:
        show_error('Não foi possível carregar os servidores')
        return
    
    servidores = [s for s in servidores_data.get('servidores', []) if s.get('ativo', True)]
    
    if not servidores:
        show_error('Nenhum servidor disponível')
        return
    
    for servidor in servidores:
        item = xbmcgui.ListItem(f"Servidor {servidor.get('id', '?')}")
        item.setArt({'icon': os.path.join(addon_path, 'icon.png')})
        url = f'plugin://{addon_id}/?action=abrir_servidor&id={servidor.get("id")}&url={servidor.get("url")}&user={servidor.get("usuario")}&pass={servidor.get("senha")}'
        xbmcplugin.addDirectoryItem(addon_handle, url, item, isFolder=False)
    
    xbmcplugin.endOfDirectory(addon_handle)

def abrir_servidor(servidor_id, url, usuario, senha):
    """Abrir servidor e listar canais"""
    try:
        # Construir URL com credenciais
        if '?' in url:
            url_completa = f"{url}&username={usuario}&password={senha}"
        else:
            url_completa = f"{url}?username={usuario}&password={senha}"
        
        # Baixar M3U
        with urllib.request.urlopen(url_completa, timeout=15) as response:
            m3u_content = response.read().decode('utf-8', errors='ignore')
        
        # Parsear M3U
        canais = []
        linhas = m3u_content.split('\n')
        i = 0
        while i < len(linhas):
            linha = linhas[i].strip()
            if linha.startswith('#EXTINF:'):
                # Extrair nome do canal
                nome = linha.split(',')[-1] if ',' in linha else 'Canal'
                # Próxima linha é a URL
                if i + 1 < len(linhas):
                    url_canal = linhas[i + 1].strip()
                    if url_canal and not url_canal.startswith('#'):
                        canais.append({'nome': nome, 'url': url_canal})
                i += 2
            else:
                i += 1
        
        if not canais:
            show_error(f'Nenhum canal encontrado no Servidor {servidor_id}')
            return
        
        # Listar canais
        for canal in canais:
            item = xbmcgui.ListItem(canal['nome'])
            item.setInfo('video', {'title': canal['nome']})
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(addon_handle, canal['url'], item, isFolder=False)
        
        xbmcplugin.endOfDirectory(addon_handle)
        log(f'Servidor {servidor_id}: {len(canais)} canais carregados')
    
    except Exception as e:
        show_error(f'Erro ao conectar ao Servidor {servidor_id}: {str(e)}')
        log(f'Erro: {str(e)}')

def menu_principal():
    """Menu principal do addon"""
    items = [
        ('TV AO VIVO', 'listar_servidores'),
        ('SAIR', 'sair')
    ]
    
    for nome, acao in items:
        item = xbmcgui.ListItem(nome)
        item.setArt({'icon': os.path.join(addon_path, 'icon.png')})
        url = f'plugin://{addon_id}/?action={acao}'
        xbmcplugin.addDirectoryItem(addon_handle, url, item, isFolder=True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def main():
    """Função principal"""
    try:
        # Pedir credenciais
        codigo, senha = pedir_credenciais()
        if not codigo or not senha:
            return
        
        # Validar cliente
        if not validar_cliente(codigo, senha):
            return
        
        # Mostrar menu principal
        menu_principal()
    
    except Exception as e:
        show_error(f'Erro: {str(e)}')
        log(f'Erro principal: {str(e)}')

if __name__ == '__main__':
    main()
