# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Plugins.Plugin import PluginDescriptor
from .Version import VERSION
from .Debug import logger
from .__init__ import _
from .PiconCockpit import PiconCockpit
from .ConfigInit import ConfigInit


def startPiconCockpit(session, **__):
    logger.info("...")
    session.open(PiconCockpit)


def Plugins(**__):
    logger.info("  +++ Version: %s starts...", VERSION)
    ConfigInit()
    return PluginDescriptor(
        name=_("PiconCockpit"),
        description=_("Manage Picons"),
        where=PluginDescriptor.WHERE_PLUGINMENU,
        icon="PiconCockpit.png", fnc=startPiconCockpit
    )
