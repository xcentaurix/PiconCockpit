# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0


import os
from Components.config import config
from Screens.MessageBox import MessageBox
from Screens.Setup import Setup
from .__init__ import _
from .Version import PLUGIN
from .Debug import logger, log_levels, setLogLevel


class SetupScreen(Setup):

    def __init__(self, session):
        Setup.__init__(self, session, setup="piconcockpit", plugin="Extensions/PiconCockpit", PluginLanguageDomain=PLUGIN)
        self.setTitle(PLUGIN + " - " + _("Setup"))

    def _applyLogLevel(self):
        setLogLevel(log_levels[config.plugins.piconcockpit.debug_log_level.value])

    def keySave(self):
        path = os.path.normpath(config.plugins.piconcockpit.picon_directory.value)
        if not os.path.exists(path):
            logger.error("Path does not exist: %s", path)
            self.session.open(MessageBox, _("Path does not exist") + ": " + path, MessageBox.TYPE_ERROR)
            return
        self._applyLogLevel()
        Setup.keySave(self)
