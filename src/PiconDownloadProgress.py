# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0


import os
from urllib.parse import urljoin

from .WebRequestsAsync import WebRequestsAsync
from .Debug import logger
from .__init__ import _
from .FileProgress import FileProgress
from .DelayTimer import DelayTimer


class PiconDownloadProgress(FileProgress):

    def __init__(self, session, picon_set_url, picons, picon_dir):
        logger.info("...")
        self.picon_set_url = picon_set_url
        self.picons = picons
        self.picon_dir = picon_dir
        self.web_client = WebRequestsAsync()
        FileProgress.__init__(self, session)
        self.setTitle(_("Picon Download") + " ...")
        self.onShow.append(self.onDialogShow)
        self.total_files = 0
        self.execution_list = self.picons
        self.status = _("Initializing") + " ..."

    def onDialogShow(self):
        logger.info("...")
        self.execPiconDownloadProgress()

    def doFileOp(self, entry):
        picon = entry
        self.file_name = picon
        self.updateProgress()
        url = None
        try:
            picon_set_url = self.picon_set_url
            if not picon_set_url.endswith('/'):
                picon_set_url += '/'
            url = urljoin(picon_set_url, picon)

            download_file = os.path.join(self.picon_dir, picon)

            logger.debug("url: %s, download_file: %s", url, download_file)

            downloader = self.web_client.downloadFileAsync(url, download_file)
            downloader.addCallback(self.downloadSuccess)
            downloader.addErrback(lambda error: self.downloadError(error, url))
            downloader.start()
        except Exception as e:
            logger.error("Error in downloadFile: %s", e)
            self.downloadError(str(e), url if url else "unknown")

    def downloadSuccess(self, _result=None):
        self.nextFileOp()

    def downloadError(self, result, url):
        logger.warning("url: %s, result: %s", url, result)
        self.nextFileOp()

    def execPiconDownloadProgress(self):
        logger.debug("...")
        if self.total_files == 0:
            self.total_files = len(self.execution_list)
        self.updateProgress()
        DelayTimer(10, self.nextFileOp)
