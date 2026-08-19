# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0

from Plugins.Plugin import PluginDescriptor
try:
    from skin import addOnLoadCallback  # OpenViX
except ImportError:
    from skin import addCallback as addOnLoadCallback  # openATV - same mechanism, different name
from .Version import VERSION
from .Debug import logger
from .__init__ import _
from .PiconCockpit import PiconCockpit
from .ConfigInit import ConfigInit
from .SkinUtils import loadPluginSkin


addOnLoadCallback(loadPluginSkin)
loadPluginSkin()  # Load on initial boot; addOnLoadCallback handles skin reloads


def openPiconCockpit(session, **__):
    logger.info("...")
    session.open(PiconCockpit)


def Plugins(**__):
    logger.info("  +++ Version: %s starts...", VERSION)
    ConfigInit()
    return PluginDescriptor(
        name=_("PiconCockpit"),
        description=_("Manage Picons"),
        where=PluginDescriptor.WHERE_PLUGINMENU,
        icon="PiconCockpit.png", fnc=openPiconCockpit
    )
