# -*- coding: utf-8 -*-
"""
BRAZTELA - Helpers do Kodi (control.py)
Autor: Braz Junior
"""
import os
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

ADDON        = xbmcaddon.Addon()
ADDON_ID     = ADDON.getAddonInfo('id')
ADDON_NAME   = ADDON.getAddonInfo('name')
ADDON_PATH   = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
ADDON_DATA   = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
ICON         = os.path.join(ADDON_PATH, 'icon.png')
FANART       = os.path.join(ADDON_PATH, 'fanart.jpg')
MEDIA        = os.path.join(ADDON_PATH, 'resources', 'media')
BACKGROUND   = os.path.join(MEDIA, 'background.jpg')

# Cores do tema
COLOR_PRIMARY   = 'FFE10600'   # vermelho BRAZTELA
COLOR_SECONDARY = 'FF0A0A0A'   # preto
COLOR_HIGHLIGHT = 'FFFFCC00'   # amarelo (para "TROCAR SERVIDOR")
COLOR_WHITE     = 'FFFFFFFF'

# Cria diretório de dados se não existir
if not os.path.exists(ADDON_DATA):
    os.makedirs(ADDON_DATA)

DIALOG   = xbmcgui.Dialog()
PROGRESS = xbmcgui.DialogProgress()


def setting(key):
    return ADDON.getSetting(key)


def set_setting(key, value):
    ADDON.setSetting(key, str(value))


def log(msg, level=xbmc.LOGINFO):
    xbmc.log('[BRAZTELA] {0}'.format(msg), level)


def notify(title, message, icon=None, time=3500):
    DIALOG.notification(title, message, icon or ICON, time, False)


def ok(title, message):
    DIALOG.ok(title, message)


def yesno(title, message, yeslabel='Sim', nolabel='Não'):
    return DIALOG.yesno(title, message, yeslabel=yeslabel, nolabel=nolabel)


def keyboard(heading, default='', hidden=False):
    kb = xbmc.Keyboard(default, heading, hidden)
    kb.doModal()
    if kb.isConfirmed():
        return kb.getText()
    return None


def numeric_input(heading, default='', hidden=True):
    """Input numérico (para PIN parental/senha)."""
    # type 0 = ShowAndGetNumber
    try:
        return DIALOG.input(heading, default, type=xbmcgui.INPUT_NUMERIC,
                            option=xbmcgui.ALPHANUM_HIDE_INPUT if hidden else 0)
    except Exception:
        return keyboard(heading, default, hidden)


def refresh():
    xbmc.executebuiltin('Container.Refresh')


def color(text, col=COLOR_PRIMARY):
    return '[COLOR {0}]{1}[/COLOR]'.format(col, text)


def bold(text):
    return '[B]{0}[/B]'.format(text)


def get_lang(code, fallback=''):
    try:
        return ADDON.getLocalizedString(code) or fallback
    except Exception:
        return fallback
