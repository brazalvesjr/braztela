#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BRAZTELA v2.0 - Addon IPTV profissional com gerenciamento pelo GitHub
Busca dinâmica de M3U/EPG, parsing inteligente de categorias, cache local
"""

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib.request
import urllib.error
import json
import os
import time
from datetime import datetime, timedelta

# Configurações
addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
addon_path = addon.getAddonInfo('path')
addon_data_path = xbmc.translatePath(f'special://profile/addon_data/{addon_id}')
cache_dir = os.path.join(addon_data_path, 'cache')
os.makedirs(cache_dir, exist_ok=True)

GITHUB_RAW = 'https://raw.githubusercontent.com/brazalvesjr/braztela/main'
SERVIDORES_URL = f'{GITHUB_RAW}/servidores_ativos.json'
CLIENTES_URL = f'{GITHUB_RAW}/clientes.json'

# Cores para debug
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

def log(msg, level='INFO'):
    """Log com cores"""
    prefix = f'[{level}]'
    if level == 'ERROR':
        print(f'{Colors.RED}{prefix} {msg}{Colors.RESET}')
    elif level == 'SUCCESS':
        print(f'{Colors.GREEN}{prefix} {msg}{Colors.RESET}')
    else:
        print(f'{Colors.YELLOW}{prefix} {msg}{Colors.RESET}')
    xbmc.log(f'{addon_id}: {msg}', xbmc.LOGINFO)

def download_json(url, timeout=10):
    """Baixar JSON do GitHub com retry"""
    for tentativa in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            log(f'Tentativa {tentativa+1}/3 falhou para {url}: {e}', 'ERROR')
            if tentativa < 2:
                time.sleep(2)
    return None

def validar_cliente(codigo, senha):
    """Validar credenciais do cliente"""
    clientes = download_json(CLIENTES_URL)
    if not clientes:
        xbmcgui.Dialog().notification('Erro', 'Não foi possível validar cliente', xbmcgui.NOTIFICATION_ERROR)
        return False
    
    for cliente in clientes.get('clientes', []):
        if cliente['codigo'] == codigo and cliente['senha'] == senha:
            if cliente.get('ativo', True):
                log(f'Cliente {codigo} validado com sucesso', 'SUCCESS')
                return True
            else:
                xbmcgui.Dialog().notification('Acesso Negado', 'Seu acesso foi bloqueado', xbmcgui.NOTIFICATION_ERROR)
                return False
    
    xbmcgui.Dialog().notification('Erro', 'Código ou senha inválidos', xbmcgui.NOTIFICATION_ERROR)
    return False

def obter_servidores_ativos():
    """Obter lista de servidores ativos do GitHub"""
    servidores = download_json(SERVIDORES_URL)
    if not servidores:
        xbmcgui.Dialog().notification('Erro', 'Não foi possível carregar servidores', xbmcgui.NOTIFICATION_ERROR)
        return []
    
    ativos = [s for s in servidores.get('servidores', []) if s.get('ativo', False) and s.get('url')]
    log(f'{len(ativos)} servidores ativos encontrados', 'SUCCESS')
    return ativos

def baixar_m3u(url, usuario, senha, timeout=15):
    """Baixar M3U do servidor IPTV"""
    try:
        url_auth = f"{url}/get.php?username={usuario}&password={senha}&type=m3u_plus&output=ts"
        req = urllib.request.Request(url_auth, headers={'User-Agent': 'VLC/3.0.0'})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        log(f'Erro ao baixar M3U: {e}', 'ERROR')
        return None

def parsear_m3u(conteudo_m3u):
    """Parsear M3U e separar em categorias"""
    canais = {'tv': [], 'filmes': [], 'series': []}
    
    if not conteudo_m3u:
        return canais
    
    linhas = conteudo_m3u.split('\n')
    i = 0
    while i < len(linhas):
        linha = linhas[i].strip()
        
        if linha.startswith('#EXTINF'):
            # Extrair informações do canal
            try:
                # Extrair nome do canal
                nome = linha.split(',')[-1].strip() if ',' in linha else 'Canal'
                
                # Extrair categoria
                categoria = 'tv'
                if 'group-title=' in linha:
                    grupo = linha.split('group-title="')[1].split('"')[0].lower()
                    if 'filme' in grupo or 'movie' in grupo:
                        categoria = 'filmes'
                    elif 'série' in grupo or 'series' in grupo or 'show' in grupo:
                        categoria = 'series'
                
                # Próxima linha é a URL
                i += 1
                if i < len(linhas):
                    url = linhas[i].strip()
                    if url and not url.startswith('#'):
                        canal = {
                            'nome': nome,
                            'url': url,
                            'categoria': categoria
                        }
                        canais[categoria].append(canal)
            except Exception as e:
                log(f'Erro ao parsear linha: {e}', 'ERROR')
        
        i += 1
    
    log(f'M3U parseado: {len(canais["tv"])} TV, {len(canais["filmes"])} Filmes, {len(canais["series"])} Séries', 'SUCCESS')
    return canais

def cache_salvar(chave, dados, ttl_horas=24):
    """Salvar dados em cache"""
    arquivo = os.path.join(cache_dir, f'{chave}.json')
    try:
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump({'dados': dados, 'timestamp': time.time()}, f)
        log(f'Cache salvo: {chave}', 'SUCCESS')
    except Exception as e:
        log(f'Erro ao salvar cache: {e}', 'ERROR')

def cache_carregar(chave, ttl_horas=24):
    """Carregar dados do cache se válido"""
    arquivo = os.path.join(cache_dir, f'{chave}.json')
    try:
        if os.path.exists(arquivo):
            with open(arquivo, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                idade = time.time() - cache['timestamp']
                if idade < (ttl_horas * 3600):
                    log(f'Cache carregado: {chave}', 'SUCCESS')
                    return cache['dados']
    except Exception as e:
        log(f'Erro ao carregar cache: {e}', 'ERROR')
    return None

def menu_principal():
    """Menu principal do addon"""
    dialog = xbmcgui.Dialog()
    
    # Solicitar código do cliente
    codigo = dialog.input('Código do Cliente', type=xbmcgui.INPUT_ALPHANUM)
    if not codigo:
        return
    
    # Solicitar senha
    senha = dialog.input('Senha', type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
    if not senha:
        return
    
    # Validar cliente
    if not validar_cliente(codigo, senha):
        return
    
    # Obter servidores ativos
    servidores = obter_servidores_ativos()
    if not servidores:
        dialog.notification('Erro', 'Nenhum servidor disponível', xbmcgui.NOTIFICATION_ERROR)
        return
    
    # Menu de seleção de servidor
    opcoes = [f'Servidor {s["id"]}' for s in servidores]
    opcoes.append('Sair')
    
    escolha = dialog.select('Selecione um Servidor', opcoes)
    if escolha < 0 or escolha >= len(servidores):
        return
    
    servidor = servidores[escolha]
    carregar_conteudo(servidor, codigo)

def carregar_conteudo(servidor, codigo):
    """Carregar conteúdo do servidor com cache"""
    dialog = xbmcgui.Dialog()
    
    chave_cache = f'servidor_{servidor["id"]}'
    conteudo = cache_carregar(chave_cache)
    
    if not conteudo:
        # Mostrar diálogo de carregamento
        dialog.notification('Carregando', f'Buscando conteúdo do Servidor {servidor["id"]}...', xbmcgui.NOTIFICATION_INFO)
        
        # Baixar M3U
        m3u = baixar_m3u(servidor['url'], servidor['usuario'], servidor['senha'])
        if not m3u:
            dialog.notification('Erro', 'Não foi possível carregar o servidor', xbmcgui.NOTIFICATION_ERROR)
            return
        
        # Parsear M3U
        conteudo = parsear_m3u(m3u)
        cache_salvar(chave_cache, conteudo)
    
    # Menu de categorias
    opcoes = []
    if conteudo['tv']:
        opcoes.append(f"📺 TV AO VIVO ({len(conteudo['tv'])})")
    if conteudo['filmes']:
        opcoes.append(f"🎬 FILMES ({len(conteudo['filmes'])})")
    if conteudo['series']:
        opcoes.append(f"📺 SÉRIES ({len(conteudo['series'])})")
    opcoes.append('← Voltar')
    
    escolha = xbmcgui.Dialog().select(f'Servidor {servidor["id"]} - Selecione', opcoes)
    
    if escolha == 0 and conteudo['tv']:
        mostrar_lista(conteudo['tv'], f'TV AO VIVO - Servidor {servidor["id"]}', servidor)
    elif escolha == 1 and conteudo['filmes']:
        mostrar_lista(conteudo['filmes'], f'FILMES - Servidor {servidor["id"]}', servidor)
    elif escolha == 2 and conteudo['series']:
        mostrar_lista(conteudo['series'], f'SÉRIES - Servidor {servidor["id"]}', servidor)

def mostrar_lista(itens, titulo, servidor):
    """Mostrar lista de canais/filmes/séries"""
    if not itens:
        xbmcgui.Dialog().notification('Vazio', 'Nenhum item disponível', xbmcgui.NOTIFICATION_INFO)
        return
    
    nomes = [item['nome'] for item in itens]
    escolha = xbmcgui.Dialog().select(titulo, nomes)
    
    if escolha >= 0:
        item = itens[escolha]
        reproduzir(item['url'], item['nome'])

def reproduzir(url, nome):
    """Reproduzir stream"""
    try:
        item = xbmcgui.ListItem(nome)
        item.setPath(url)
        xbmcplugin.setResolvedUrl(int(xbmc.getInfoLabel('System.CurrentControlId')), True, item)
        
        # Usar ffmpeg se disponível para melhor compatibilidade
        player = xbmc.Player()
        player.play(url)
        log(f'Reproduzindo: {nome}', 'SUCCESS')
    except Exception as e:
        log(f'Erro ao reproduzir: {e}', 'ERROR')
        xbmcgui.Dialog().notification('Erro', 'Não foi possível reproduzir', xbmcgui.NOTIFICATION_ERROR)

if __name__ == '__main__':
    menu_principal()
