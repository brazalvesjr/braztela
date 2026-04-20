# -*- coding: utf-8 -*-
"""
BRAZTELA - Gerador de advancedsettings.xml otimizado
Autor: Braz Junior

Cria (ou atualiza) o arquivo advancedsettings.xml no userdata do Kodi
com valores otimizados para streaming ao vivo e VOD, reduzindo travamentos.
"""
import os
import xbmcvfs
from . import control

CACHE_PROFILES = {
    '0': 50 * 1024 * 1024,    # 50 MB
    '1': 100 * 1024 * 1024,   # 100 MB
    '2': 150 * 1024 * 1024,   # 150 MB (recomendado)
    '3': 250 * 1024 * 1024,   # 250 MB
}


def path():
    return xbmcvfs.translatePath('special://userdata/advancedsettings.xml')


def write():
    cache_profile = control.setting('cache_size') or '2'
    cache_bytes   = CACHE_PROFILES.get(cache_profile, CACHE_PROFILES['2'])

    xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<advancedsettings>
    <!-- BRAZTELA - otimização anti-travamento -->
    <cache>
        <memorysize>{cache}</memorysize>
        <buffermode>1</buffermode>
        <readfactor>5</readfactor>
    </cache>
    <network>
        <buffermode>1</buffermode>
        <cachemembuffersize>{cache}</cachemembuffersize>
        <readbufferfactor>20</readbufferfactor>
        <curlclienttimeout>30</curlclienttimeout>
        <curllowspeedtime>20</curllowspeedtime>
    </network>
    <videolibrary>
        <recentlyaddeditems>50</recentlyaddeditems>
    </videolibrary>
    <pvr>
        <minvideocachelevel>25</minvideocachelevel>
        <minaudiocachelevel>25</minaudiocachelevel>
        <cacheindvdplayer>true</cacheindvdplayer>
        <timeshiftbuffer>4</timeshiftbuffer>
    </pvr>
    <gui>
        <algorithmdirtyregions>3</algorithmdirtyregions>
        <nofliptimeout>1000</nofliptimeout>
    </gui>
</advancedsettings>
'''.format(cache=cache_bytes)

    try:
        p = path()
        # Backup se existir
        if os.path.exists(p):
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    old = f.read()
                with open(p + '.bak', 'w', encoding='utf-8') as f:
                    f.write(old)
            except Exception:
                pass
        with open(p, 'w', encoding='utf-8') as f:
            f.write(xml)
        control.notify(
            control.ADDON_NAME,
            'advancedsettings.xml gravado! Reinicie o Kodi para aplicar.'
        )
        control.ok(
            control.ADDON_NAME,
            '[B]advancedsettings.xml[/B] gravado com sucesso em:\n[COLOR FFE10600]{0}[/COLOR]\n\n'
            'Para aplicar as otimizações anti-travamento, [B]reinicie o Kodi[/B] agora.'
            .format(p)
        )
        return True
    except Exception as e:
        control.log('advanced_cfg.write error: {0}'.format(e))
        control.ok(control.ADDON_NAME,
                   'Não foi possível gravar advancedsettings.xml.\n{0}'.format(e))
        return False
