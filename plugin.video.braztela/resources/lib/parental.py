# -*- coding: utf-8 -*-
"""
BRAZTELA - Controle Parental
Autor: Braz Junior
"""
from . import control, tools

ADULT_KEYWORDS_DEFAULT = [
    'xxx', 'adult', 'adults', 'porn', 'porno', '+18', '18+',
    'erotic', 'erotico', 'erótico', 'sex', 'sexy', 'hot'
]


def _repo_url(path):
    base = control.setting('repo_base_url') or \
           'https://raw.githubusercontent.com/brazjunior/braztela/main/'
    if not base.endswith('/'):
        base += '/'
    return base + path


def adult_keywords():
    """Busca lista remota de palavras adultas (ou usa default)."""
    data = tools.cache_get('parental', ttl_minutes=120)
    if not data:
        data = tools.http_json(_repo_url('parental.json')) or {}
        if data:
            tools.cache_set('parental', data)
    kws = data.get('adult_keywords') or ADULT_KEYWORDS_DEFAULT
    return [k.lower() for k in kws]


def is_adult(name):
    n = (name or '').lower()
    return any(k in n for k in adult_keywords())


def should_hide_adult():
    return control.setting('hide_adult') == 'true'


def enabled():
    return control.setting('parental_enabled') == 'true'


def current_pin():
    return control.setting('parental_pin') or '0000'


def ensure_initial_pin():
    """Se PIN ainda é 0000 (default), pede para cliente criar um."""
    if current_pin() == '0000':
        control.ok(control.ADDON_NAME,
                   'Configure um PIN de 4 dígitos para o\n'
                   '[B]Controle Parental[/B].\n'
                   'Este PIN protegerá conteúdo adulto e configurações.')
        p1 = control.numeric_input('Novo PIN (4 dígitos)')
        if not p1 or len(p1) != 4 or not p1.isdigit():
            control.notify(control.ADDON_NAME, 'PIN inválido. Usando 0000.')
            return
        p2 = control.numeric_input('Confirme o PIN')
        if p1 != p2:
            control.notify(control.ADDON_NAME, 'PINs não conferem.')
            return
        control.set_setting('parental_pin', p1)
        control.notify(control.ADDON_NAME, 'PIN parental configurado com sucesso.')


def ask_pin(reason='Conteúdo protegido'):
    """Pede PIN. Retorna True se correto."""
    if not enabled():
        return True
    pin = control.numeric_input('{0} — Digite o PIN'.format(reason))
    if pin and pin == current_pin():
        return True
    control.notify(control.ADDON_NAME, 'PIN incorreto.')
    return False


def change_pin():
    if not ask_pin('Alterar PIN'):
        return
    p1 = control.numeric_input('Novo PIN (4 dígitos)')
    if not p1 or len(p1) != 4 or not p1.isdigit():
        return
    p2 = control.numeric_input('Confirme o Novo PIN')
    if p1 != p2:
        control.notify(control.ADDON_NAME, 'PINs não conferem.')
        return
    control.set_setting('parental_pin', p1)
    control.notify(control.ADDON_NAME, 'PIN alterado com sucesso.')
