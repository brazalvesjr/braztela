#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xbmcgui
import xbmcplugin
import sys
import urllib.parse as urlparse

# Dados embutidos - Clientes
CLIENTES = {
    "TESTE": {"senha": "123456", "nome": "Teste", "ativo": True},
    "CLIENTE001": {"senha": "senha123456", "nome": "João Silva", "ativo": True},
    "CLIENTE002": {"senha": "acesso2026", "nome": "Maria Santos", "ativo": True},
    "CLIENTE003": {"senha": "premium789", "nome": "Carlos Oliveira", "ativo": True},
    "CLIENTE004": {"senha": "streaming001", "nome": "Ana Costa", "ativo": True},
    "CLIENTE005": {"senha": "braztela2026", "nome": "Pedro Ferreira", "ativo": True},
}

# Dados embutidos - Servidores
SERVIDORES = [
    {"nome": "Premium HD 1", "dns": "http://servidor1.com:8080", "ativo": True},
    {"nome": "Premium HD 2", "dns": "http://servidor2.com:8080", "ativo": True},
    {"nome": "4K Ultra", "dns": "http://servidor3.com:8080", "ativo": True},
    {"nome": "Backup 1", "dns": "http://servidor4.com:8080", "ativo": True},
    {"nome": "Backup 2", "dns": "http://servidor5.com:8080", "ativo": True},
    {"nome": "Reserva 1", "dns": "http://servidor6.com:8080", "ativo": False},
    {"nome": "Reserva 2", "dns": "http://servidor7.com:8080", "ativo": False},
    {"nome": "Reserva 3", "dns": "http://servidor8.com:8080", "ativo": False},
    {"nome": "Reserva 4", "dns": "http://servidor9.com:8080", "ativo": False},
    {"nome": "Reserva 5", "dns": "http://servidor10.com:8080", "ativo": False},
]

def show_login():
    """Tela de login"""
    dialog = xbmcgui.Dialog()
    
    # Pedir código do cliente
    codigo = dialog.input("Código do Cliente", type=xbmcgui.INPUT_ALPHANUMERIC)
    if not codigo:
        return False
    
    # Pedir senha
    senha = dialog.input("Senha de Acesso", type=xbmcgui.INPUT_PASSWORD)
    if not senha:
        return False
    
    # Validar
    if codigo in CLIENTES:
        cliente = CLIENTES[codigo]
        if cliente["senha"] == senha and cliente["ativo"]:
            dialog.notification("BRAZTELA", "Bem-vindo, " + cliente["nome"] + "!", xbmcgui.NOTIFICATION_INFO, 3000)
            return True
        else:
            dialog.notification("BRAZTELA", "Código ou senha inválidos!", xbmcgui.NOTIFICATION_ERROR, 3000)
            return False
    else:
        dialog.notification("BRAZTELA", "Cliente não encontrado!", xbmcgui.NOTIFICATION_ERROR, 3000)
        return False

def show_menu():
    """Menu principal"""
    dialog = xbmcgui.Dialog()
    opcoes = [
        "📺 TV ao Vivo",
        "🎬 Filmes",
        "📺 Séries",
        "🖥️ Trocar Servidor",
        "🔒 Controle Parental",
        "⚙️ Configurações"
    ]
    
    escolha = dialog.select("BRAZTELA - Menu Principal", opcoes)
    
    if escolha == 0:
        xbmcgui.Dialog().notification("BRAZTELA", "TV ao Vivo - Em desenvolvimento", xbmcgui.NOTIFICATION_INFO, 2000)
    elif escolha == 1:
        xbmcgui.Dialog().notification("BRAZTELA", "Filmes - Em desenvolvimento", xbmcgui.NOTIFICATION_INFO, 2000)
    elif escolha == 2:
        xbmcgui.Dialog().notification("BRAZTELA", "Séries - Em desenvolvimento", xbmcgui.NOTIFICATION_INFO, 2000)
    elif escolha == 3:
        show_servers()
    elif escolha == 4:
        xbmcgui.Dialog().notification("BRAZTELA", "Controle Parental - Em desenvolvimento", xbmcgui.NOTIFICATION_INFO, 2000)
    elif escolha == 5:
        xbmcgui.Dialog().notification("BRAZTELA", "Configurações - Em desenvolvimento", xbmcgui.NOTIFICATION_INFO, 2000)

def show_servers():
    """Mostrar lista de servidores"""
    dialog = xbmcgui.Dialog()
    servidores_ativos = [s["nome"] for s in SERVIDORES if s["ativo"]]
    
    if not servidores_ativos:
        dialog.notification("BRAZTELA", "Nenhum servidor disponível", xbmcgui.NOTIFICATION_ERROR, 2000)
        return
    
    escolha = dialog.select("Selecione um Servidor", servidores_ativos)
    if escolha >= 0:
        servidor = servidores_ativos[escolha]
        dialog.notification("BRAZTELA", "Servidor: " + servidor, xbmcgui.NOTIFICATION_INFO, 2000)

def main():
    """Função principal"""
    if show_login():
        show_menu()

if __name__ == "__main__":
    main()
