# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0

from Plugins.Plugin import PluginDescriptor
from .Version import PLUGIN, VERSION
from .Debug import logger
from .__init__ import _
from .PiconCockpit import PiconCockpit
from . import ConfigInit  # noqa: F401, pylint: disable=unused-import
from .SkinUtils import loadPluginSkin


loadPluginSkin(PLUGIN)


def openPiconCockpit(session, **__):
    logger.info("...")
    session.open(PiconCockpit)


def Plugins(**__):
    logger.info("  +++ Version: %s starts...", VERSION)
    descriptors = [
        PluginDescriptor(
            name=_("PiconCockpit"),
            description=_("Manage Picons"),
            where=PluginDescriptor.WHERE_PLUGINMENU,
            icon="PiconCockpit.png", fnc=openPiconCockpit,
            needsRestart=True
        ),
    ]
    try:
        descriptors += [
            PluginDescriptor(
                where=PluginDescriptor.WHERE_SKINCHANGE,
                fnc=loadPluginSkin
            )
        ]
    except Exception:
        pass

    return descriptors
