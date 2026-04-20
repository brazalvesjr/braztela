# -*- coding: utf-8 -*-
"""
BRAZTELA - Autenticação por senha individual de cliente
Autor: Braz Junior

Cada cliente recebe um par (código + senha) gerado pelo Braz Junior no
passwords.json do GitHub. O addon valida localmente contra essa lista remota.
"""
import hashlib
import time
from datetime import datetime

from . import control, tools


def _repo_url(path):
    base = control.setting('repo_base_url') or \
           'https://raw.githubusercontent.com/brazjunior/braztela/main/'
    if not base.endswith('/'):
        base += '/'
    return base + path


def load_passwords(force=False):
    """Busca passwords.json remoto com cache curto."""
    if force:
        tools.cache_clear()
    cached = tools.cache_get('passwords', ttl_minutes=15)
    if cached and not force:
        return cached
    data = tools.http_json(_repo_url('passwords.json'))
    if data:
        tools.cache_set('passwords', data)
    return data


def _hash_session(code, pwd):
    raw = '{0}|{1}|braztela'.format(code, pwd).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def is_authenticated():
    """Verifica se já existe sessão válida salva localmente."""
    token = control.setting('session_token')
    code  = control.setting('client_code')
    pwd   = control.setting('client_password')
    exp   = control.setting('client_expires')
    if not (token and code and pwd):
        return False
    if _hash_session(code, pwd) != token:
        return False
    # Verifica expiração local
    if exp:
        try:
            d = datetime.strptime(exp, '%Y-%m-%d')
            if datetime.now() > d:
                control.log('Sessão expirada localmente')
                return False
        except Exception:
            pass
    return True


def login_prompt():
    """Mostra diálogo de login e valida contra o passwords.json remoto."""
    control.ok(
        control.ADDON_NAME,
        '[B][COLOR FFE10600]Bem-vindo ao BRAZTELA[/COLOR][/B]\n\n'
        'Informe seu Código de Cliente e Senha de Acesso.\n'
        '(Fornecidos por Braz Junior)'
    )

    code = control.keyboard('Código do Cliente')
    if not code:
        return False
    pwd = control.keyboard('Senha de Acesso', hidden=True)
    if not pwd:
        return False

    return validate(code.strip(), pwd.strip())


def validate(code, pwd):
    """Valida (code, pwd) contra o passwords.json remoto."""
    data = load_passwords(force=True)
    if not data or 'passwords' not in data:
        control.ok(control.ADDON_NAME,
                   'Não foi possível baixar a lista de senhas do servidor.\n'
                   'Verifique sua conexão e tente novamente.')
        return False

    code_up = code.upper()
    for entry in data['passwords']:
        if str(entry.get('code', '')).upper() == code_up and \
           str(entry.get('password', '')) == pwd:
            if not entry.get('active', True):
                control.ok(control.ADDON_NAME,
                           'Sua conta está DESATIVADA.\n'
                           'Entre em contato com o suporte.')
                return False
            # Verifica expiração
            exp = entry.get('expires', '')
            if exp:
                try:
                    d = datetime.strptime(exp, '%Y-%m-%d')
                    if datetime.now() > d:
                        control.ok(control.ADDON_NAME,
                                   'Sua conta EXPIROU em {0}.\n'
                                   'Renove seu acesso com o suporte.'
                                   .format(exp))
                        return False
                except Exception:
                    pass
            # Autenticado
            control.set_setting('client_code', code_up)
            control.set_setting('client_password', pwd)
            control.set_setting('client_label', entry.get('label', ''))
            control.set_setting('client_expires', exp or '')
            control.set_setting('session_token', _hash_session(code_up, pwd))
            control.notify(control.ADDON_NAME,
                           'Bem-vindo, {0}!'.format(entry.get('label') or code_up))
            return True

    control.ok(control.ADDON_NAME,
               'Código ou senha [B]inválidos[/B].\n'
               'Verifique seus dados e tente novamente.')
    return False


def logout():
    for k in ('client_code', 'client_password', 'client_label',
              'client_expires', 'session_token',
              'xtream_username', 'xtream_password',
              'active_server_id', 'active_server_name'):
        control.set_setting(k, '')
    tools.cache_clear()
    control.notify(control.ADDON_NAME, 'Sessão encerrada com sucesso.')
