# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
from urllib.parse import urljoin

from .WebRequestsAsync import WebRequestsAsync
from .Debug import logger
from .__init__ import _
from .FileProgress import FileProgress
from .DelayTimer import DelayTimer
from .FileUtils import readFile
from .SkinUtils import getSkinPath


class PiconDownloadProgress(FileProgress):
    skin = readFile(getSkinPath("PiconDownloadProgress.xml"))

    def __init__(self, session, picon_set_url, picons, picon_dir):
        logger.debug("...")
        self.picon_set_url = picon_set_url
        self.picons = picons
        self.picon_dir = picon_dir
        # Initialize WebRequestsAsync client
        self.web_client = WebRequestsAsync()
        FileProgress.__init__(self, session)
        self.setTitle(_("Picon Download") + " ...")
        self.execution_list = []
        self.onShow.append(self.onDialogShow)

    def onDialogShow(self):
        logger.debug("...")
        self.execPiconDownloadProgress()

    def doFileOp(self, entry):
        picon = entry
        self.file_name = picon
        self.status = _("Please wait") + " ..."
        self.updateProgress()
        url = None
        try:
            # Proper URL construction for picon download
            picon_set_url = str(self.picon_set_url)
            if not picon_set_url.endswith('/'):
                picon_set_url += '/'
            url = urljoin(picon_set_url, str(picon))

            download_file = os.path.join(str(self.picon_dir), str(picon))

            logger.debug("url: %s, download_file: %s", url, download_file)

            # Use WebRequestsAsync instead of twisted downloadPage
            downloader = self.web_client.downloadFileAsync(url, download_file)
            downloader.addCallback(self.downloadSuccess)
            downloader.addErrback(lambda error: self.downloadError(error, url))
            downloader.start()
        except Exception as e:
            logger.error("Error in downloadFile: %s", e)
            self.downloadError(str(e), url if url else "unknown")

    def downloadSuccess(self, _result=None):
        # logger.info("...")
        self.nextFileOp()

    def downloadError(self, result, url):
        logger.info("url: %s, result: %s", url, result)
        self.nextFileOp()

    def execPiconDownloadProgress(self):
        logger.debug("...")
        self.status = _("Initializing") + " ..."
        self.updateProgress()
        self.execution_list = self.picons
        self.total_files = len(self.execution_list)
        DelayTimer(10, self.nextFileOp)
