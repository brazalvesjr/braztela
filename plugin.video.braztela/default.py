#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BRAZTELA v2.0 - Addon IPTV com gerenciamento pelo GitHub
"""

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib.request
import json
import os
import time

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
addon_path = addon.getAddonInfo('path')
addon_data_path = xbmc.translatePath('special://profile/addon_data/{0}'.format(addon_id))
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
                log_debug('Cliente {0} validado'.format(codigo))
                return True
            else:
                xbmcgui.Dialog().notification('Acesso Negado', 'Seu acesso foi bloqueado', xbmcgui.NOTIFICATION_ERROR)
                return False
    
    xbmcgui.Dialog().notification('Erro', 'Codigo ou senha invalidos', xbmcgui.NOTIFICATION_ERROR)
    return False

def obter_servidores_ativos():
    """Obter servidores ativos"""
    servidores_data = download_json(SERVIDORES_URL)
    if not servidores_data:
        xbmcgui.Dialog().notification('Erro', 'Nao foi possivel carregar servidores', xbmcgui.NOTIFICATION_ERROR)
        return []
    
    ativos = []
    for s in servidores_data.get('servidores', []):
        if s.get('ativo', False) and s.get('url'):
            ativos.append(s)
    
    log_debug('{0} servidores ativos'.format(len(ativos)))
    return ativos

def baixar_m3u(url, usuario, senha):
    """Baixar M3U do servidor"""
    try:
        url_m3u = '{0}/get.php?username={1}&password={2}&type=m3u_plus&output=ts'.format(url, usuario, senha)
        req = urllib.request.Request(url_m3u, headers={'User-Agent': 'VLC/3.0.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        log_debug('Erro ao baixar M3U: {0}'.format(str(e)))
        return None

def parsear_m3u(conteudo):
    """Parsear M3U em categorias"""
    canais = {'tv': [], 'filmes': [], 'series': []}
    
    if not conteudo:
        return canais
    
    linhas = conteudo.split('\n')
    i = 0
    
    while i < len(linhas):
        linha = linhas[i].strip()
        
        if linha.startswith('#EXTINF'):
            try:
                nome = 'Canal'
                if ',' in linha:
                    nome = linha.split(',')[-1].strip()
                
                categoria = 'tv'
                if 'group-title=' in linha:
                    grupo = linha.split('group-title="')[1].split('"')[0].lower()
                    if 'filme' in grupo or 'movie' in grupo:
                        categoria = 'filmes'
                    elif 'serie' in grupo or 'series' in grupo or 'show' in grupo:
                        categoria = 'series'
                
                i += 1
                if i < len(linhas):
                    url = linhas[i].strip()
                    if url and not url.startswith('#'):
                        canal = {'nome': nome, 'url': url}
                        canais[categoria].append(canal)
            except:
                pass
        
        i += 1
    
    return canais

def cache_salvar(chave, dados):
    """Salvar cache"""
    try:
        arquivo = os.path.join(cache_dir, '{0}.json'.format(chave))
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump({'dados': dados, 'timestamp': time.time()}, f)
    except:
        pass

def cache_carregar(chave, ttl_horas=24):
    """Carregar cache"""
    try:
        arquivo = os.path.join(cache_dir, '{0}.json'.format(chave))
        if os.path.exists(arquivo):
            with open(arquivo, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                idade = time.time() - cache.get('timestamp', 0)
                if idade < (ttl_horas * 3600):
                    return cache.get('dados')
    except:
        pass
    return None

def menu_principal():
    """Menu principal"""
    dialog = xbmcgui.Dialog()
    
    codigo = dialog.input('Codigo do Cliente', type=xbmcgui.INPUT_ALPHANUM)
    if not codigo:
        return
    
    senha = dialog.input('Senha', type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
    if not senha:
        return
    
    if not validar_cliente(codigo, senha):
        return
    
    servidores = obter_servidores_ativos()
    if not servidores:
        dialog.notification('Erro', 'Nenhum servidor disponivel', xbmcgui.NOTIFICATION_ERROR)
        return
    
    opcoes = ['Servidor {0}'.format(s['id']) for s in servidores]
    opcoes.append('Sair')
    
    escolha = dialog.select('Selecione um Servidor', opcoes)
    if escolha < 0 or escolha >= len(servidores):
        return
    
    servidor = servidores[escolha]
    carregar_conteudo(servidor)

def carregar_conteudo(servidor):
    """Carregar conteudo do servidor"""
    dialog = xbmcgui.Dialog()
    
    chave = 'servidor_{0}'.format(servidor['id'])
    conteudo = cache_carregar(chave)
    
    if not conteudo:
        dialog.notification('Carregando', 'Buscando conteudo...', xbmcgui.NOTIFICATION_INFO)
        
        m3u = baixar_m3u(servidor['url'], servidor['usuario'], servidor['senha'])
        if not m3u:
            dialog.notification('Erro', 'Nao foi possivel carregar o servidor', xbmcgui.NOTIFICATION_ERROR)
            return
        
        conteudo = parsear_m3u(m3u)
        cache_salvar(chave, conteudo)
    
    opcoes = []
    if conteudo.get('tv'):
        opcoes.append('TV AO VIVO ({0})'.format(len(conteudo['tv'])))
    if conteudo.get('filmes'):
        opcoes.append('FILMES ({0})'.format(len(conteudo['filmes'])))
    if conteudo.get('series'):
        opcoes.append('SERIES ({0})'.format(len(conteudo['series'])))
    opcoes.append('Voltar')
    
    escolha = dialog.select('Servidor {0}'.format(servidor['id']), opcoes)
    
    if escolha == 0 and conteudo.get('tv'):
        mostrar_lista(conteudo['tv'], 'TV AO VIVO')
    elif escolha == 1 and conteudo.get('filmes'):
        mostrar_lista(conteudo['filmes'], 'FILMES')
    elif escolha == 2 and conteudo.get('series'):
        mostrar_lista(conteudo['series'], 'SERIES')

def mostrar_lista(itens, titulo):
    """Mostrar lista de itens"""
    if not itens:
        xbmcgui.Dialog().notification('Vazio', 'Nenhum item disponivel', xbmcgui.NOTIFICATION_INFO)
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
        player = xbmc.Player()
        player.play(url)
        log_debug('Reproduzindo: {0}'.format(nome))
    except Exception as e:
        log_debug('Erro ao reproduzir: {0}'.format(str(e)))
        xbmcgui.Dialog().notification('Erro', 'Nao foi possivel reproduzir', xbmcgui.NOTIFICATION_ERROR)

if __name__ == '__main__':
    try:
        menu_principal()
    except Exception as e:
        log_debug('Erro geral: {0}'.format(str(e)))
        xbmcgui.Dialog().notification('Erro', 'Erro ao executar addon', xbmcgui.NOTIFICATION_ERROR)
