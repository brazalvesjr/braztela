# -*- coding: utf-8 -*-
"""
BRAZTELA - Gerenciador de Servidores (servers.json via GitHub)
Autor: Braz Junior
"""
from . import control, tools


def _repo_url(path):
    base = control.setting('repo_base_url') or \
           'https://raw.githubusercontent.com/brazjunior/braztela/main/'
    if not base.endswith('/'):
        base += '/'
    return base + path


def load_servers(force=False):
    cached = tools.cache_get('servers', ttl_minutes=int(
        control.setting('cache_minutes') or 60))
    if cached and not force:
        return cached
    data = tools.http_json(_repo_url('servers.json'))
    if data:
        tools.cache_set('servers', data)
    return data or {'servers': []}


def active_server():
    """Retorna dict do servidor ativo ou None."""
    sid = control.setting('active_server_id')
    if not sid or sid == '0':
        return None
    try:
        sid = int(sid)
    except Exception:
        return None
    data = load_servers()
    for s in data.get('servers', []):
        if int(s.get('id', 0)) == sid:
            return s
    return None


def choose_server():
    """Diálogo que lista servidores e permite escolher o ativo."""
    data = load_servers(force=True)
    servers = [s for s in data.get('servers', []) if s.get('active', True)]
    if not servers:
        control.ok(control.ADDON_NAME,
                   'Nenhum servidor disponível no momento.\n'
                   'Braz Junior irá cadastrar os servidores em breve.')
        return False

    current = active_server()
    labels = []
    for s in servers:
        prefix = '[COLOR FFFFCC00]> ATIVO <[/COLOR] ' if current and \
                 int(current['id']) == int(s['id']) else ''
        note = ' — ' + s['note'] if s.get('note') else ''
        labels.append('{0}{1}{2}'.format(prefix, s.get('name', 'Servidor'), note))

    idx = control.DIALOG.select('[COLOR FFE10600]Selecione o Servidor[/COLOR]',
                                labels)
    if idx < 0:
        return False

    chosen = servers[idx]
    control.set_setting('active_server_id', str(chosen['id']))
    control.set_setting('active_server_name', chosen.get('name', ''))

    # Limpa credenciais Xtream do servidor anterior
    control.set_setting('xtream_username', '')
    control.set_setting('xtream_password', '')

    # Pede credenciais do novo servidor
    user = control.keyboard('Usuário do Painel ({0})'.format(chosen.get('name')))
    if not user:
        return False
    pwd = control.keyboard('Senha do Painel', hidden=True)
    if not pwd:
        return False
    control.set_setting('xtream_username', user.strip())
    control.set_setting('xtream_password', pwd.strip())

    # Testa autenticação
    if test_server(chosen['dns'], user.strip(), pwd.strip()):
        control.notify(control.ADDON_NAME,
                       'Servidor {0} conectado!'.format(chosen.get('name')))
        tools.cache_clear()
        control.refresh()
        return True
    else:
        control.ok(control.ADDON_NAME,
                   'Falha ao autenticar no servidor selecionado.\n'
                   'Verifique o usuário e senha do painel.')
        return False


def test_server(dns, user, pwd):
    url = '{0}/player_api.php?username={1}&password={2}'.format(
        dns.rstrip('/'), user, pwd)
    data = tools.http_json(url, timeout=10, retries=2)
    if not data:
        return False
    try:
        return int(data.get('user_info', {}).get('auth', 0)) == 1
    except Exception:
        return False


def current_credentials():
    """(dns, user, pwd) do servidor ativo ou (None, None, None)."""
    srv = active_server()
    if not srv:
        return (None, None, None)
    dns = srv.get('dns', '').rstrip('/')
    user = control.setting('xtream_username')
    pwd = control.setting('xtream_password')
    if not (dns and user and pwd):
        return (None, None, None)
    return (dns, user, pwd)
