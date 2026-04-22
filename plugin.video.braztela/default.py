#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import json
import os
from urllib.parse import urlencode, parse_qs

# Configurações do addon
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_VERSION = ADDON.getAddonInfo('version')
HANDLE = int(sys.argv[1])

# ===== DADOS EMBUTIDOS =====
# Senhas dos clientes (você pode editar aqui ou via GitHub depois)
PASSWORDS_DATA = {
    "clients": [
        {"code": "TESTE", "password": "123456", "name": "Cliente Teste", "expiry": "2027-12-31", "active": True},
        {"code": "CLIENTE001", "password": "senha001", "name": "Cliente 1", "expiry": "2027-12-31", "active": True},
        {"code": "CLIENTE002", "password": "senha002", "name": "Cliente 2", "expiry": "2027-12-31", "active": True},
        {"code": "CLIENTE003", "password": "senha003", "name": "Cliente 3", "expiry": "2027-12-31", "active": True},
        {"code": "CLIENTE004", "password": "senha004", "name": "Cliente 4", "expiry": "2027-12-31", "active": True},
        {"code": "CLIENTE005", "password": "senha005", "name": "Cliente 5", "expiry": "2027-12-31", "active": True},
    ]
}

# 20 Servidores
SERVERS_DATA = {
    "servers": [
        {"id": 1, "name": "🔴 Premium HD 1", "dns": "", "port": 8080, "note": "Servidor Premium - Alta qualidade"},
        {"id": 2, "name": "🔴 Premium HD 2", "dns": "", "port": 8080, "note": "Servidor Premium - Backup"},
        {"id": 3, "name": "🟡 4K Ultra 1", "dns": "", "port": 8080, "note": "Servidor 4K - Ultra HD"},
        {"id": 4, "name": "🟡 4K Ultra 2", "dns": "", "port": 8080, "note": "Servidor 4K - Backup"},
        {"id": 5, "name": "🟢 Streaming 1", "dns": "", "port": 8080, "note": "Servidor Streaming - Rápido"},
        {"id": 6, "name": "🟢 Streaming 2", "dns": "", "port": 8080, "note": "Servidor Streaming - Backup"},
        {"id": 7, "name": "🔵 Internacional 1", "dns": "", "port": 8080, "note": "Servidor Internacional"},
        {"id": 8, "name": "🔵 Internacional 2", "dns": "", "port": 8080, "note": "Servidor Internacional - Backup"},
        {"id": 9, "name": "🟣 Backup 1", "dns": "", "port": 8080, "note": "Servidor Backup"},
        {"id": 10, "name": "🟣 Backup 2", "dns": "", "port": 8080, "note": "Servidor Backup"},
        {"id": 11, "name": "⚪ Reserva 1", "dns": "", "port": 8080, "note": "Servidor Reserva"},
        {"id": 12, "name": "⚪ Reserva 2", "dns": "", "port": 8080, "note": "Servidor Reserva"},
        {"id": 13, "name": "🟠 Teste 1", "dns": "", "port": 8080, "note": "Servidor Teste"},
        {"id": 14, "name": "🟠 Teste 2", "dns": "", "port": 8080, "note": "Servidor Teste"},
        {"id": 15, "name": "🔶 Espelho 1", "dns": "", "port": 8080, "note": "Servidor Espelho"},
        {"id": 16, "name": "🔶 Espelho 2", "dns": "", "port": 8080, "note": "Servidor Espelho"},
        {"id": 17, "name": "🟥 Emergência 1", "dns": "", "port": 8080, "note": "Servidor Emergência"},
        {"id": 18, "name": "🟥 Emergência 2", "dns": "", "port": 8080, "note": "Servidor Emergência"},
        {"id": 19, "name": "⬛ Secundário 1", "dns": "", "port": 8080, "note": "Servidor Secundário"},
        {"id": 20, "name": "⬛ Secundário 2", "dns": "", "port": 8080, "note": "Servidor Secundário"},
    ]
}

# Palavras-chave para controle parental
PARENTAL_DATA = {
    "keywords": [
        "adulto", "pornô", "sexo", "nude", "xxx", "18+", "erótico",
        "violência extrema", "gore", "sangue", "assassinato",
        "drogas", "cocaína", "maconha", "heroína"
    ]
}

def log(msg):
    """Log de debug"""
    try:
        xbmcaddon.Addon().log(f"[{ADDON_NAME}] {msg}", xbmcaddon.LOGINFO)
    except:
        pass

def show_notification(title, msg, duration=5000, notification_type=xbmcgui.NOTIFICATION_INFO):
    """Exibe notificação na tela"""
    try:
        dialog = xbmcgui.Dialog()
        dialog.notification(title, msg, notification_type, duration)
    except:
        pass

def show_dialog(title, msg):
    """Exibe diálogo de texto"""
    try:
        dialog = xbmcgui.Dialog()
        dialog.ok(title, msg)
    except:
        pass

def keyboard_input(prompt="", default="", hidden=False):
    """Entrada de teclado"""
    try:
        dialog = xbmcgui.Dialog()
        return dialog.input(prompt, default, xbmcgui.INPUT_ALPHANUM if not hidden else xbmcgui.INPUT_PASSWORD)
    except:
        return ""

def add_menu_item(label, action, params=None, icon=None, is_folder=True):
    """Adiciona um item ao menu"""
    try:
        url = f"plugin://{ADDON_ID}/?action={action}"
        if params:
            url += "&" + urlencode(params)
        
        item = xbmcgui.ListItem(label)
        if icon:
            item.setArt({'icon': icon, 'fanart': icon})
        
        xbmcplugin.addDirectoryItem(HANDLE, url, item, is_folder)
    except Exception as e:
        log(f"Erro ao adicionar item: {str(e)}")

def main_menu():
    """Menu principal"""
    log("=== BRAZTELA INICIADO ===")
    
    try:
        icon_live = f"file://{ADDON_PATH}/resources/media/icon_live.png"
        icon_movies = f"file://{ADDON_PATH}/resources/media/icon_movies.png"
        icon_series = f"file://{ADDON_PATH}/resources/media/icon_series.png"
        icon_server = f"file://{ADDON_PATH}/resources/media/icon_server.png"
        icon_parental = f"file://{ADDON_PATH}/resources/media/icon_parental.png"
        icon_settings = f"file://{ADDON_PATH}/resources/media/icon_settings.png"
        
        add_menu_item("📺 TV ao Vivo", "live", icon=icon_live)
        add_menu_item("🎬 Filmes", "movies", icon=icon_movies)
        add_menu_item("📺 Séries", "series", icon=icon_series)
        add_menu_item("🖥️ Trocar Servidor", "servers", icon=icon_server)
        add_menu_item("🔒 Controle Parental", "parental", icon=icon_parental)
        add_menu_item("⚙️ Configurações", "settings", icon=icon_settings)
        
        xbmcplugin.endOfDirectory(HANDLE)
        log("Menu principal carregado com sucesso")
        
    except Exception as e:
        log(f"Erro no menu principal: {str(e)}")
        show_notification("Erro", f"Erro: {str(e)}", notification_type=xbmcgui.NOTIFICATION_ERROR)

def live_menu():
    """Menu de TV ao Vivo"""
    log("Abrindo TV ao Vivo")
    
    try:
        item = xbmcgui.ListItem("📡 Conectando ao servidor...")
        xbmcplugin.addDirectoryItem(HANDLE, "", item, False)
        xbmcplugin.endOfDirectory(HANDLE)
        show_notification("Info", "Funcionalidade em desenvolvimento")
    except Exception as e:
        log(f"Erro: {str(e)}")

def movies_menu():
    """Menu de Filmes"""
    log("Abrindo Filmes")
    
    try:
        item = xbmcgui.ListItem("🎬 Filmes em desenvolvimento...")
        xbmcplugin.addDirectoryItem(HANDLE, "", item, False)
        xbmcplugin.endOfDirectory(HANDLE)
        show_notification("Info", "Funcionalidade em desenvolvimento")
    except Exception as e:
        log(f"Erro: {str(e)}")

def series_menu():
    """Menu de Séries"""
    log("Abrindo Séries")
    
    try:
        item = xbmcgui.ListItem("📺 Séries em desenvolvimento...")
        xbmcplugin.addDirectoryItem(HANDLE, "", item, False)
        xbmcplugin.endOfDirectory(HANDLE)
        show_notification("Info", "Funcionalidade em desenvolvimento")
    except Exception as e:
        log(f"Erro: {str(e)}")

def servers_menu():
    """Menu de seleção de servidor"""
    log("Abrindo menu de servidores")
    
    try:
        for server in SERVERS_DATA["servers"]:
            label = f"{server['name']} - {server['note']}"
            item = xbmcgui.ListItem(label)
            item.setInfo('video', {'plot': f"Porta: {server['port']}"})
            xbmcplugin.addDirectoryItem(HANDLE, "", item, False)
        
        xbmcplugin.endOfDirectory(HANDLE)
        show_notification("Servidores", "20 servidores disponíveis")
        
    except Exception as e:
        log(f"Erro: {str(e)}")

def parental_menu():
    """Menu de controle parental"""
    log("Abrindo controle parental")
    
    try:
        item = xbmcgui.ListItem("🔒 Controle parental ativo")
        item.setInfo('video', {'plot': f"Palavras-chave bloqueadas: {len(PARENTAL_DATA['keywords'])}"})
        xbmcplugin.addDirectoryItem(HANDLE, "", item, False)
        xbmcplugin.endOfDirectory(HANDLE)
        
    except Exception as e:
        log(f"Erro: {str(e)}")

def settings_menu():
    """Abre as configurações do addon"""
    log("Abrindo configurações")
    try:
        ADDON.openSettings()
    except Exception as e:
        log(f"Erro: {str(e)}")

def authenticate():
    """Autenticação do cliente"""
    log("Iniciando autenticação")
    
    try:
        # Solicitar código do cliente
        code = keyboard_input("Código do Cliente:", "")
        if not code:
            show_notification("Erro", "Código não fornecido")
            return False
        
        # Verificar se o código existe
        client = None
        for c in PASSWORDS_DATA["clients"]:
            if c["code"].upper() == code.upper():
                client = c
                break
        
        if not client:
            show_notification("Erro", "Código de cliente inválido")
            log(f"Código inválido: {code}")
            return False
        
        if not client["active"]:
            show_notification("Erro", "Cliente desativado")
            return False
        
        # Solicitar senha
        password = keyboard_input("Senha de Acesso:", "", hidden=True)
        if not password:
            show_notification("Erro", "Senha não fornecida")
            return False
        
        # Verificar senha
        if password != client["password"]:
            show_notification("Erro", "Senha incorreta")
            log(f"Senha incorreta para: {code}")
            return False
        
        # Autenticação bem-sucedida
        show_notification("Sucesso", f"Bem-vindo {client['name']}!")
        log(f"Cliente autenticado: {code}")
        
        # Salvar informações da sessão
        ADDON.setSetting("cliente_autenticado", code)
        ADDON.setSetting("cliente_nome", client["name"])
        
        return True
        
    except Exception as e:
        log(f"Erro na autenticação: {str(e)}")
        show_notification("Erro", f"Erro: {str(e)}", notification_type=xbmcgui.NOTIFICATION_ERROR)
        return False

# Roteador principal
if __name__ == '__main__':
    try:
        # Parse dos parâmetros
        params = parse_qs(sys.argv[2].lstrip('?'))
        action = params.get('action', ['main'])[0]
        
        log(f"Ação: {action}")
        
        # Verificar autenticação (exceto para ações específicas)
        if action not in ['main', 'settings'] and action != 'auth':
            cliente = ADDON.getSetting("cliente_autenticado")
            if not cliente:
                if not authenticate():
                    main_menu()
                    sys.exit(0)
        
        # Roteamento
        if action == 'main':
            main_menu()
        elif action == 'live':
            live_menu()
        elif action == 'movies':
            movies_menu()
        elif action == 'series':
            series_menu()
        elif action == 'servers':
            servers_menu()
        elif action == 'parental':
            parental_menu()
        elif action == 'settings':
            settings_menu()
        else:
            main_menu()
            
    except Exception as e:
        log(f"Erro fatal: {str(e)}")
        try:
            dialog = xbmcgui.Dialog()
            dialog.notification("BRAZTELA - Erro", f"Erro: {str(e)}", xbmcgui.NOTIFICATION_ERROR)
        except:
            pass
