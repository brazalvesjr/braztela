# -*- coding: utf-8 -*-
"""
BRAZTELA - Cliente Xtream Codes
Autor: Braz Junior

Implementa as chamadas padrão do Xtream Codes para TV ao vivo,
filmes (VOD) e séries, com metadados completos (sinopse, capa, ano, etc).
"""
from . import control, tools, servers


def _api(action=None, extra=None):
    dns, user, pwd = servers.current_credentials()
    if not dns:
        return None
    base = '{0}/player_api.php?username={1}&password={2}'.format(dns, user, pwd)
    if action:
        base += '&action={0}'.format(action)
    if extra:
        for k, v in extra.items():
            base += '&{0}={1}'.format(k, v)
    return base


def panel():
    dns, user, pwd = servers.current_credentials()
    if not dns:
        return None
    return tools.http_json(
        '{0}/panel_api.php?username={1}&password={2}'.format(dns, user, pwd))


# =============================================================
#   LIVE TV
# =============================================================
def live_categories():
    url = _api('get_live_categories')
    return tools.http_json(url) if url else []


def live_streams(category_id=None):
    extra = {'category_id': category_id} if category_id else None
    url = _api('get_live_streams', extra)
    return tools.http_json(url) if url else []


def live_stream_url(stream_id, ext='ts'):
    dns, user, pwd = servers.current_credentials()
    if not dns:
        return None
    # m3u8 preferido para player adaptativo; fallback ts
    return '{0}/live/{1}/{2}/{3}.{4}'.format(dns, user, pwd, stream_id, ext)


def live_stream_m3u8(stream_id):
    dns, user, pwd = servers.current_credentials()
    if not dns:
        return None
    return '{0}/live/{1}/{2}/{3}.m3u8'.format(dns, user, pwd, stream_id)


# =============================================================
#   VOD (Filmes)
# =============================================================
def vod_categories():
    url = _api('get_vod_categories')
    return tools.http_json(url) if url else []


def vod_streams(category_id=None):
    extra = {'category_id': category_id} if category_id else None
    url = _api('get_vod_streams', extra)
    return tools.http_json(url) if url else []


def vod_info(vod_id):
    url = _api('get_vod_info', {'vod_id': vod_id})
    return tools.http_json(url) if url else {}


def movie_stream_url(stream_id, ext='mp4'):
    dns, user, pwd = servers.current_credentials()
    if not dns:
        return None
    return '{0}/movie/{1}/{2}/{3}.{4}'.format(dns, user, pwd, stream_id, ext)


# =============================================================
#   SÉRIES
# =============================================================
def series_categories():
    url = _api('get_series_categories')
    return tools.http_json(url) if url else []


def series_list(category_id=None):
    extra = {'category_id': category_id} if category_id else None
    url = _api('get_series', extra)
    return tools.http_json(url) if url else []


def series_info(series_id):
    url = _api('get_series_info', {'series_id': series_id})
    return tools.http_json(url) if url else {}


def episode_stream_url(episode_id, ext='mp4'):
    dns, user, pwd = servers.current_credentials()
    if not dns:
        return None
    return '{0}/series/{1}/{2}/{3}.{4}'.format(dns, user, pwd, episode_id, ext)


# =============================================================
#   Helpers de metadados (sinopse + extras)
# =============================================================
def extract_movie_meta(stream, full_info=None):
    """Extrai metadados completos (com sinopse) de um filme VOD."""
    info = (full_info or {}).get('info', {}) if full_info else {}
    movie = (full_info or {}).get('movie_data', {}) if full_info else {}

    title = stream.get('name') or movie.get('name') or info.get('name') or ''
    plot = (info.get('plot') or info.get('description') or
            stream.get('plot') or '')
    year = (info.get('releasedate', '') or '')[:4] if info.get('releasedate') \
        else (info.get('year') or '')
    rating = info.get('rating') or stream.get('rating') or ''
    duration_s = info.get('duration_secs') or 0
    if not duration_s and info.get('duration'):
        # "01:33:00" -> segundos
        try:
            parts = info['duration'].split(':')
            if len(parts) == 3:
                duration_s = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        except Exception:
            duration_s = 0
    genre = info.get('genre') or ''
    cast = info.get('cast') or info.get('actors') or ''
    director = info.get('director') or ''
    poster = (info.get('movie_image') or info.get('cover_big') or
              stream.get('stream_icon') or '')
    fanart = ''
    if info.get('backdrop_path'):
        bp = info['backdrop_path']
        if isinstance(bp, list) and bp:
            fanart = bp[0]
        elif isinstance(bp, str):
            fanart = bp
    mpaa = info.get('mpaa_rating') or ''
    release = info.get('releasedate') or ''

    return {
        'title': title,
        'plot': plot or 'Sinopse indisponível.',
        'year': year,
        'rating': rating,
        'duration': duration_s,
        'genre': genre,
        'cast': cast,
        'director': director,
        'poster': poster,
        'fanart': fanart,
        'mpaa': mpaa,
        'releasedate': release,
    }


def extract_series_meta(serie):
    """Metadados de série a partir do item da lista."""
    info = serie.get('info') if isinstance(serie.get('info'), dict) else {}
    plot = (serie.get('plot') or info.get('plot') or
            serie.get('description') or '')
    poster = serie.get('cover') or info.get('cover') or ''
    fanart = ''
    bp = serie.get('backdrop_path')
    if isinstance(bp, list) and bp:
        fanart = bp[0]
    elif isinstance(bp, str):
        fanart = bp
    release = serie.get('releaseDate') or serie.get('release_date') or ''
    return {
        'title': serie.get('name') or '',
        'plot': plot or 'Sinopse indisponível.',
        'year': (release or '')[:4],
        'rating': serie.get('rating') or '',
        'genre': serie.get('genre') or '',
        'cast': serie.get('cast') or '',
        'director': serie.get('director') or '',
        'poster': poster,
        'fanart': fanart,
        'releasedate': release,
    }


def extract_episode_meta(ep, series_info_data=None):
    """Metadados de episódio + fallback do info da série."""
    info = ep.get('info') if isinstance(ep.get('info'), dict) else {}
    serie_info = (series_info_data or {}).get('info') or {}
    plot = info.get('plot') or info.get('overview') or serie_info.get('plot') or ''
    poster = info.get('movie_image') or info.get('cover_big') or \
             serie_info.get('cover') or ''
    fanart = ''
    bp = serie_info.get('backdrop_path')
    if isinstance(bp, list) and bp:
        fanart = bp[0]
    duration_s = info.get('duration_secs') or 0
    if not duration_s and info.get('duration'):
        try:
            parts = info['duration'].split(':')
            if len(parts) == 3:
                duration_s = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        except Exception:
            duration_s = 0
    release = info.get('releasedate') or info.get('air_date') or ''
    return {
        'title': ep.get('title') or 'Episódio',
        'plot': plot or 'Sinopse indisponível.',
        'year': (release or '')[:4],
        'rating': info.get('rating') or '',
        'duration': duration_s,
        'genre': serie_info.get('genre') or '',
        'cast': serie_info.get('cast') or '',
        'poster': poster,
        'fanart': fanart or serie_info.get('cover') or '',
        'releasedate': release,
    }
