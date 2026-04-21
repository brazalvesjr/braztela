# -*- coding: utf-8 -*-
"""
BRAZTELA - Addon para Kodi
Autor: Braz Junior
Versão: 1.0.0

Roteador principal. Gerencia menus, navegação, autenticação,
controle parental e playback via player avançado anti-travamento.
"""
import os
import sys

# Garantir que o diretório do addon esteja no path
ADDON_PATH = os.path.dirname(os.path.abspath(__file__))
if ADDON_PATH not in sys.path:
    sys.path.insert(0, ADDON_PATH)

from resources.lib import (
    control, tools, auth, servers, parental, xtream, player, advanced_cfg
)


# =============================================================
#   MENUS
# =============================================================
def home():
    """Tela principal do addon."""
    # Ícones do menu
    MEDIA = control.MEDIA
    ic = {
        'server':   os.path.join(MEDIA, 'icon_server.png'),
        'live':     os.path.join(MEDIA, 'icon_live.png'),
        'movies':   os.path.join(MEDIA, 'icon_movies.png'),
        'series':   os.path.join(MEDIA, 'icon_series.png'),
        'guide':    os.path.join(MEDIA, 'icon_guide.png'),
        'search':   os.path.join(MEDIA, 'icon_search.png'),
        'parental': os.path.join(MEDIA, 'icon_parental.png'),
        'account':  os.path.join(MEDIA, 'icon_account.png'),
        'settings': os.path.join(MEDIA, 'icon_settings.png'),
    }

    srv = servers.active_server()
    srv_label = srv.get('name') if srv else 'Nenhum selecionado'

    # 1) TROCAR SERVIDOR - destaque amarelo (primeira posição)
    trocar_label = '[B][COLOR FFFFCC00]>>> TROCAR SERVIDOR <<<[/COLOR][/B] ' \
                   '[COLOR FFFFFFFF]({0})[/COLOR]'.format(srv_label)
    tools.add_dir(trocar_label, {'mode': 'choose_server'},
                  icon=ic['server'], fanart=control.FANART,
                  description='Escolha qual servidor usar. Há vários servidores '
                              'disponíveis. Se um estiver lento, troque para outro.')

    if not srv:
        # Sem servidor escolhido ainda — não mostra demais categorias
        tools.add_dir('[B][COLOR FFE10600]— Selecione um servidor acima para começar —[/COLOR][/B]',
                      {'mode': 'choose_server'}, icon=ic['server'],
                      description='Você precisa escolher um servidor antes de '
                                  'acessar os conteúdos.')
        tools.add_dir('Minha Conta', {'mode': 'account'},
                      icon=ic['account'], description='Informações da sua assinatura.')
        tools.add_dir('Configurações', {'mode': 'settings'},
                      icon=ic['settings'], description='Ajustes do addon.')
        tools.add_dir('Sair (Logout)', {'mode': 'logout'},
                      icon=ic['account'], description='Encerrar sessão atual.')
        tools.end_directory()
        return

    # Menu principal completo
    tools.add_dir('[B]TV AO VIVO[/B]', {'mode': 'live_cats'},
                  icon=ic['live'], description='Canais de TV ao vivo em HD/FHD.')
    tools.add_dir('[B]FILMES[/B]', {'mode': 'vod_cats'},
                  icon=ic['movies'], description='Catálogo de filmes com sinopse, '
                                                 'capa, elenco e avaliação.')
    tools.add_dir('[B]SÉRIES[/B]', {'mode': 'series_cats'},
                  icon=ic['series'], description='Séries, novelas e animes '
                                                 'organizados por temporadas.')
    tools.add_dir('Controle Parental', {'mode': 'parental'},
                  icon=ic['parental'], description='Gerenciar PIN e bloqueios.')
    tools.add_dir('Minha Conta', {'mode': 'account'},
                  icon=ic['account'], description='Detalhes da sua assinatura.')
    tools.add_dir('Configurações', {'mode': 'settings'},
                  icon=ic['settings'], description='Ajustes avançados, player, '
                                                   'buffer e reconexão.')
    tools.add_dir('Sair (Logout)', {'mode': 'logout'},
                  icon=ic['account'], description='Encerrar sessão atual.')
    tools.end_directory()


# =============================================================
#   TV AO VIVO
# =============================================================
def live_cats():
    cats = xtream.live_categories() or []
    if not cats:
        control.notify(control.ADDON_NAME, 'Nenhuma categoria encontrada.')
    for c in cats:
        name = c.get('category_name', '')
        if parental.should_hide_adult() and parental.is_adult(name):
            continue
        tools.add_dir(name,
                      {'mode': 'live_channels',
                       'cat': str(c.get('category_id', ''))},
                      icon=os.path.join(control.MEDIA, 'icon_live.png'),
                      description='Canais da categoria {0}.'.format(name))
    tools.end_directory()


def live_channels(category_id):
    chans = xtream.live_streams(category_id) or []
    for ch in chans:
        name = ch.get('name', '')
        if parental.should_hide_adult() and parental.is_adult(name):
            continue
        stream_id = ch.get('stream_id')
        icon = ch.get('stream_icon') or os.path.join(control.MEDIA, 'icon_live.png')
        epg = ch.get('epg_channel_id') or ''
        plot = 'Canal ao vivo: {0}\nEPG: {1}'.format(name, epg or '—')
        tools.add_dir(name,
                      {'mode': 'play_live', 'sid': str(stream_id),
                       'title': name, 'icon': icon},
                      icon=icon, description=plot, is_folder=False,
                      meta={'poster': icon})
    tools.end_directory()


# =============================================================
#   FILMES (VOD)
# =============================================================
def vod_cats():
    cats = xtream.vod_categories() or []
    for c in cats:
        name = c.get('category_name', '')
        if parental.should_hide_adult() and parental.is_adult(name):
            if not parental.ask_pin_if_needed(name):
                continue
        tools.add_dir(name,
                      {'mode': 'vod_list', 'cat': str(c.get('category_id', ''))},
                      icon=os.path.join(control.MEDIA, 'icon_movies.png'),
                      description='Filmes da categoria {0}.'.format(name))
    tools.end_directory()


def vod_list(category_id):
    movies = xtream.vod_streams(category_id) or []
    for m in movies:
        name = m.get('name', '')
        if parental.should_hide_adult() and parental.is_adult(name):
            continue
        meta = xtream.extract_movie_meta(m)
        plot = meta['plot']
        stream_id = m.get('stream_id')
        ext = m.get('container_extension') or 'mp4'
        tools.add_dir(name,
                      {'mode': 'play_movie', 'sid': str(stream_id),
                       'ext': ext, 'title': name},
                      icon=meta.get('poster') or control.ICON,
                      fanart=meta.get('fanart') or control.FANART,
                      description=plot, is_folder=False, meta=meta)
    tools.end_directory(content='movies')


# =============================================================
#   SÉRIES
# =============================================================
def series_cats():
    cats = xtream.series_categories() or []
    for c in cats:
        name = c.get('category_name', '')
        if parental.should_hide_adult() and parental.is_adult(name):
            continue
        tools.add_dir(name,
                      {'mode': 'series_list', 'cat': str(c.get('category_id', ''))},
                      icon=os.path.join(control.MEDIA, 'icon_series.png'),
                      description='Séries da categoria {0}.'.format(name))
    tools.end_directory()


def series_list(category_id):
    items = xtream.series_list(category_id) or []
    for s in items:
        name = s.get('name', '')
        if parental.should_hide_adult() and parental.is_adult(name):
            continue
        meta = xtream.extract_series_meta(s)
        tools.add_dir(name,
                      {'mode': 'series_seasons',
                       'sid': str(s.get('series_id', ''))},
                      icon=meta.get('poster') or control.ICON,
                      fanart=meta.get('fanart') or control.FANART,
                      description=meta['plot'], meta=meta)
    tools.end_directory(content='tvshows')


def series_seasons(series_id):
    info = xtream.series_info(series_id) or {}
    seasons = info.get('episodes') or {}
    serie_meta = info.get('info') or {}
    fanart = ''
    bp = serie_meta.get('backdrop_path')
    if isinstance(bp, list) and bp:
        fanart = bp[0]
    for season_num in sorted(seasons.keys(), key=lambda x: int(x) if str(x).isdigit() else 0):
        eps = seasons[season_num]
        first_ep = eps[0] if eps else {}
        poster = (first_ep.get('info') or {}).get('movie_image') or \
                 serie_meta.get('cover') or control.ICON
        plot = serie_meta.get('plot') or 'Temporada {0}'.format(season_num)
        tools.add_dir('Temporada {0}'.format(season_num),
                      {'mode': 'series_episodes', 'sid': str(series_id),
                       'season': str(season_num)},
                      icon=poster,
                      fanart=fanart or control.FANART,
                      description=plot,
                      meta={'poster': poster, 'fanart': fanart,
                            'plot': plot})
    tools.end_directory(content='seasons')


def series_episodes(series_id, season):
    info = xtream.series_info(series_id) or {}
    seasons = info.get('episodes') or {}
    eps = seasons.get(str(season)) or []
    for ep in eps:
        meta = xtream.extract_episode_meta(ep, info)
        ext = ep.get('container_extension') or 'mp4'
        title = '{0}. {1}'.format(ep.get('episode_num', ''),
                                  meta['title'])
        tools.add_dir(title,
                      {'mode': 'play_episode',
                       'sid': str(ep.get('id', '')),
                       'ext': ext, 'title': title},
                      icon=meta.get('poster') or control.ICON,
                      fanart=meta.get('fanart') or control.FANART,
                      description=meta['plot'], is_folder=False, meta=meta)
    tools.end_directory(content='episodes')


# =============================================================
#   PLAYBACK
# =============================================================
def play_live(stream_id, title='', icon=''):
    # Preferir m3u8 para InputStream Adaptive
    url = xtream.live_stream_m3u8(stream_id)
    meta = {'plot': 'Transmissão ao vivo', 'poster': icon or control.ICON}
    player.resolve_and_play(url, title or 'Ao Vivo', meta=meta, is_live=True)


def play_movie(stream_id, ext='mp4', title=''):
    url = xtream.movie_stream_url(stream_id, ext)
    # Buscar metadados detalhados
    info = xtream.vod_info(stream_id)
    meta = xtream.extract_movie_meta({'name': title}, info)
    player.resolve_and_play(url, title, meta=meta, is_live=False)


def play_episode(stream_id, ext='mp4', title=''):
    url = xtream.episode_stream_url(stream_id, ext)
    player.resolve_and_play(url, title, meta={'plot': title}, is_live=False)


# =============================================================
#   OUTROS
# =============================================================
def account():
    data = xtream.panel() or {}
    ui = data.get('user_info', {})
    si = data.get('server_info', {})
    from datetime import datetime
    exp = ui.get('exp_date')
    try:
        exp_txt = datetime.fromtimestamp(int(exp)).strftime('%d/%m/%Y %H:%M') if exp else 'Ilimitado'
    except Exception:
        exp_txt = 'Ilimitado'
    lines = [
        ('Cliente', control.setting('client_label') or control.setting('client_code')),
        ('Servidor', control.setting('active_server_name')),
        ('Usuário do Painel', ui.get('username', '—')),
        ('Status', ui.get('status', '—')),
        ('Expira em', exp_txt),
        ('Conexões Ativas', '{0} / {1}'.format(
            ui.get('active_cons', '—'),
            ui.get('max_connections', '—'))),
        ('Servidor URL', si.get('url', '—')),
        ('Fuso Horário', si.get('timezone', '—')),
    ]
    for label, value in lines:
        tools.add_dir('[B]{0}:[/B] {1}'.format(label, value),
                      {'mode': 'noop'},
                      icon=os.path.join(control.MEDIA, 'icon_account.png'),
                      description='', is_folder=False)
    tools.end_directory()


def parental_menu():
    if parental.enabled() and not parental.ask_pin('Controle Parental'):
        return
    tools.add_dir('Alterar PIN', {'mode': 'parental_change'},
                  icon=os.path.join(control.MEDIA, 'icon_parental.png'),
                  description='Trocar o PIN de 4 dígitos.', is_folder=False)
    tools.add_dir('{0} Controle Parental ({1})'.format(
                    'Desativar' if parental.enabled() else 'Ativar',
                    'ATIVO' if parental.enabled() else 'INATIVO'),
                  {'mode': 'parental_toggle'},
                  icon=os.path.join(control.MEDIA, 'icon_parental.png'),
                  description='Liga/desliga o controle parental.', is_folder=False)
    tools.add_dir('{0} Conteúdo Adulto ({1})'.format(
                    'Mostrar' if parental.should_hide_adult() else 'Ocultar',
                    'OCULTO' if parental.should_hide_adult() else 'VISÍVEL'),
                  {'mode': 'parental_adult_toggle'},
                  icon=os.path.join(control.MEDIA, 'icon_parental.png'),
                  description='Mostra ou oculta conteúdo adulto.', is_folder=False)
    tools.end_directory()


# Extensão do parental para menus
def _ask_pin_if_needed(name):
    if parental.should_hide_adult() and parental.is_adult(name):
        return parental.ask_pin('Conteúdo Adulto')
    return True
parental.ask_pin_if_needed = _ask_pin_if_needed


def settings_menu():
    if control.setting('parental_settings') == 'true' and parental.enabled():
        if not parental.ask_pin('Configurações protegidas'):
            return
    control.ADDON.openSettings()


# =============================================================
#   ROTEADOR
# =============================================================
def router():
    params = tools.get_params()
    mode = params.get('mode', '')

    # Modos que não requerem autenticação
    if mode == 'logout':
        auth.logout()
        control.refresh()
        return
    if mode == 'write_advanced':
        advanced_cfg.write()
        return
    if mode == 'refresh_cache':
        tools.cache_clear()
        control.notify(control.ADDON_NAME, 'Cache limpo. Atualizando...')
        control.refresh()
        return

    # Checar autenticação
    if not auth.is_authenticated():
        if not auth.login_prompt():
            return
        parental.ensure_initial_pin()
        control.refresh()
        return

    # Modos internos
    if not mode:
        home(); return
    if mode == 'choose_server':
        servers.choose_server(); return
    if mode == 'live_cats':
        live_cats(); return
    if mode == 'live_channels':
        live_channels(params.get('cat', '')); return
    if mode == 'vod_cats':
        vod_cats(); return
    if mode == 'vod_list':
        vod_list(params.get('cat', '')); return
    if mode == 'series_cats':
        series_cats(); return
    if mode == 'series_list':
        series_list(params.get('cat', '')); return
    if mode == 'series_seasons':
        series_seasons(params.get('sid', '')); return
    if mode == 'series_episodes':
        series_episodes(params.get('sid', ''), params.get('season', '1')); return
    if mode == 'play_live':
        play_live(params.get('sid', ''), params.get('title', ''),
                  params.get('icon', '')); return
    if mode == 'play_movie':
        play_movie(params.get('sid', ''), params.get('ext', 'mp4'),
                   params.get('title', '')); return
    if mode == 'play_episode':
        play_episode(params.get('sid', ''), params.get('ext', 'mp4'),
                     params.get('title', '')); return
    if mode == 'account':
        account(); return
    if mode == 'parental':
        parental_menu(); return
    if mode == 'parental_change':
        parental.change_pin(); return
    if mode == 'parental_toggle':
        new_val = 'false' if parental.enabled() else 'true'
        control.set_setting('parental_enabled', new_val)
        control.refresh(); return
    if mode == 'parental_adult_toggle':
        new_val = 'false' if parental.should_hide_adult() else 'true'
        control.set_setting('hide_adult', new_val)
        control.refresh(); return
    if mode == 'settings':
        settings_menu(); return
    if mode == 'noop':
        return

    # Fallback
    home()


if __name__ == '__main__':
    router()
