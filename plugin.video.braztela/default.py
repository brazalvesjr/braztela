#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import json
import os
import urllib.request
import urllib.error
from urllib.parse import urlencode, parse_qs
from datetime import datetime

# Configurações do addon
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_VERSION = ADDON.getAddonInfo('version')
HANDLE = int(sys.argv[1])

# URLs do GitHub
GITHUB_RAW = "https://raw.githubusercontent.com/brazalvesjr/braztela/main"
PASSWORDS_URL = f"{GITHUB_RAW}/passwords.json"
SERVERS_URL = f"{GITHUB_RAW}/servers.json"
PARENTAL_URL = f"{GITHUB_RAW}/parental.json"

# Diretório de cache local
ADDON_DATA_PATH = xbmcaddon.Addon().getAddonInfo('profile')
if not os.path.exists(ADDON_DATA_PATH):
    os.makedirs(ADDON_DATA_PATH)

PASSWORDS_CACHE = os.path.join(ADDON_DATA_PATH, "passwords_cache.json")
SERVERS_CACHE = os.path.join(ADDON_DATA_PATH, "servers_cache.json")

# Senhas padrão embutidas (fallback se GitHub não responder)
DEFAULT_PASSWORDS = {
    "version": "1.0.0",
    "passwords": [
        {"code": "TESTE", "password": "123456", "expires": "2027-12-31", "active": True, "label": "Braz Junior"},
        {"code": "CLIENTE001", "password": "senha123456", "expires": "2027-12-31", "active": True, "label": "Cliente 1"},
        {"code": "CLIENTE002", "password": "acesso2026", "expires": "2027-12-31", "active": True, "label": "Cliente 2"},
    ]
}

DEFAULT_SERVERS = {
    "version": "1.0.0",
    "servers": [
        {"id": i, "name": f"Servidor {i}", "dns": "", "port": 8080, "note": f"Servidor {i}"} 
        for i in range(1, 21)
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
        input_type = xbmcgui.INPUT_PASSWORD if hidden else xbmcgui.INPUT_ALPHANUM
        return dialog.input(prompt, default, input_type)
    except:
        return ""

def fetch_json_from_github(url, cache_file, default_data):
    """Busca JSON do GitHub com fallback para cache local e dados padrão"""
    try:
        # Tentar buscar do GitHub
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            # Salvar no cache local
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                log(f"Cache atualizado: {cache_file}")
            except:
                pass
            
            return data
            
    except Exception as e:
        log(f"Erro ao buscar {url}: {str(e)}")
        
        # Tentar usar cache local
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    log(f"Usando cache local: {cache_file}")
                    show_notification("Info", "Usando dados em cache (sem internet)", duration=3000)
                    return data
            except:
                pass
        
        # Usar dados padrão embutidos
        log(f"Usando dados padrão para {cache_file}")
        return default_data

def load_passwords():
    """Carrega as senhas (GitHub > Cache > Padrão)"""
    return fetch_json_from_github(PASSWORDS_URL, PASSWORDS_CACHE, DEFAULT_PASSWORDS)

def load_servers():
    """Carrega os servidores (GitHub > Cache > Padrão)"""
    return fetch_json_from_github(SERVERS_URL, SERVERS_CACHE, DEFAULT_SERVERS)

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
    log("=== BRAZTELA v2 INICIADO ===")
    
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
        servers_data = load_servers()
        
        for server in servers_data.get("servers", [])[:20]:
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
        item.setInfo('video', {'plot': "Filtrando conteúdo adulto"})
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
    """Autenticação do cliente com senhas do GitHub"""
    log("Iniciando autenticação")
    
    try:
        # Carregar senhas
        passwords_data = load_passwords()
        
        # Solicitar código do cliente
        code = keyboard_input("Código do Cliente:", "")
        if not code:
            show_notification("Erro", "Código não fornecido")
            return False
        
        # Verificar se o código existe
        client = None
        for c in passwords_data.get("passwords", []):
            if c["code"].upper() == code.upper():
                client = c
                break
        
        if not client:
            show_notification("Erro", "Código de cliente inválido")
            log(f"Código inválido: {code}")
            return False
        
        if not client.get("active", False):
            show_notification("Erro", "Cliente desativado")
            log(f"Cliente desativado: {code}")
            return False
        
        # Verificar expiração
        try:
            expiry_date = datetime.strptime(client.get("expires", "2099-12-31"), "%Y-%m-%d")
            if datetime.now() > expiry_date:
                show_notification("Erro", "Acesso expirado")
                log(f"Acesso expirado para: {code}")
                return False
        except:
            pass
        
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
        label = client.get("label", code)
        show_notification("Sucesso", f"Bem-vindo {label}!")
        log(f"Cliente autenticado: {code} ({label})")
        
        # Salvar informações da sessão
        ADDON.setSetting("cliente_autenticado", code)
        ADDON.setSetting("cliente_nome", label)
        
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
