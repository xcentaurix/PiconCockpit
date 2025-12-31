# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
import uuid
from urllib.parse import urljoin, urlparse, quote

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.Pixmap import Pixmap
from Components.Button import Button
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Components.Sources.List import List
from Components.config import config, configfile
from Tools.LoadPixmap import LoadPixmap

from .ServiceDataCompat import getServiceList, getTVBouquets, getRadioBouquets
from .WebRequestsAsync import WebRequestsAsync
from .Debug import logger
from .__init__ import _
from .FileUtils import readFile, createDirectory
from .ConfigScreen import ConfigScreen
from .PiconDownloadProgress import PiconDownloadProgress
from .ConfigInit import ConfigInit
from .SkinUtils import getSkinPath


picon_info_file = "picon_info.txt"
picon_list_file = "zz_picon_list.txt"


class PiconCockpit(Screen):
    skin = readFile(getSkinPath("PiconCockpit.xml"))

    def __init__(self, session):
        logger.info("...")
        Screen.__init__(self, session)

        self.web_client = WebRequestsAsync()

        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "MenuActions"],
            {
                "menu": self.openConfigScreen,
                "cancel": self.exit,
                "red": self.exit,
                "green": self.green,
            },
            prio=-1
        )

        self.last_picon_set = config.plugins.piconcockpit.last_picon_set.value
        self.setTitle(_("PiconCockpit"))
        self["list"] = List()
        self["preview"] = Pixmap()
        self["key_menu"] = Button(_("Menu"))
        self["key_green"] = Button(_("Download"))
        self["key_red"] = Button(_("Exit"))
        self["key_menu"] = StaticText()
        self.first_start = True
        self.onLayoutFinish.append(self.__onLayoutFinish)
        self.onClose.append(self.__onClose)

    def onSelectionChanged(self):
        logger.info("...")
        self.downloadPreview()

    def __onLayoutFinish(self):
        logger.info("...")
        self.picon_dir = config.plugins.piconcockpit.picon_directory.value
        if not os.path.exists(self.picon_dir):
            createDirectory(self.picon_dir)

        # Connect selection changed callback for Components.Sources.List
        self["list"].onSelectionChanged.append(self.onSelectionChanged)

        if self.first_start:
            self.first_start = False
            self.getPiconSetInfo()
        else:
            self.createList(False)

    def __onClose(self):
        logger.info("...")
        # Disconnect selection changed callback to prevent memory leaks
        try:
            self["list"].onSelectionChanged.remove(self.onSelectionChanged)
        except (ValueError, AttributeError):
            # Callback might not be in list or list might not exist
            pass

    def getPiconSetInfo(self):
        logger.info("...")
        try:
            # Get server URL and clean it
            server_url = config.plugins.piconcockpit.picon_server.value

            # Clean and validate URL using standard functions
            server_url = str(server_url).strip()

            # Ensure proper protocol
            if not server_url.startswith(('http://', 'https://')):
                server_url = 'http://' + server_url

            # Parse and validate URL
            parsed = urlparse(server_url)
            if not parsed.netloc:
                raise ValueError(f"Invalid URL format: {server_url}")

            # Construct URL using urllib.parse.urljoin for RFC 3986 compliance
            if not server_url.endswith('/'):
                server_url += '/'
            base_url = urljoin(server_url, "picons/")
            url = urljoin(base_url, str(picon_info_file))
            # Ensure proper file path handling
            download_file = os.path.join(str(self.picon_dir), str(picon_info_file))

            # Validate file path
            if not os.path.isdir(self.picon_dir):
                logger.warning("Picon directory does not exist: %s", self.picon_dir)

            # Validate URL format before calling downloadPage
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid URL format: {url}")

            # Ensure URL and file path are plain strings (not bytes) for Python 3 Twisted
            url = str(url)
            download_file = str(download_file)

            # Use WebRequestsAsync instead of twisted downloadPage
            downloader = self.web_client.downloadFileAsync(url, download_file)
            downloader.addCallback(self.gotPiconSetInfo).addErrback(self.downloadError)
            downloader.start()
        except Exception as e:
            logger.error("Error in getPiconSetInfo: %s", e)
            # Don't show modal dialog during initialization, just create empty list
            self.createList(False)

    def gotPiconSetInfo(self, _result):
        logger.info("...")
        self.createList(True)
        self.onSelectionChanged()

    def downloadError(self, failure, url=None):
        logger.info("...")
        if url:
            logger.error("url: %s, failure: %s", url, failure)
        else:
            logger.error("Download failed: %s", failure)
        # Don't show modal dialog during initialization - defer it
        self.onLayoutFinish.append(lambda: self.showErrorMessage(_(
            "Picon server access failed")))
        self.createList(False)

    def showErrorMessage(self, message):
        """Show error message in a non-blocking way"""
        logger.info("...")
        try:
            self.session.open(MessageBox, message, MessageBox.TYPE_ERROR)
        except Exception as e:
            # If we still can't show modal, just log it
            logger.error("Could not show error message: %s, error: %s", message, e)

    def openConfigScreen(self):
        logger.info("...")
        picon_set = self["list"].getCurrent()
        if picon_set:
            self.last_picon_set = picon_set[4]
        self.session.openWithCallback(
            self.openConfigScreenCallback, ConfigScreen, config.plugins.piconcockpit)

    def openConfigScreenCallback(self, _result=None):
        logger.info("...")
        self.first_start = True
        self.__onLayoutFinish()

    def exit(self):
        logger.info("...")
        picon_set = self["list"].getCurrent()
        if picon_set:
            logger.debug("last_picon_set: %s", picon_set[4])
            config.plugins.piconcockpit.last_picon_set.value = picon_set[4]
            config.plugins.piconcockpit.last_picon_set.save()

        # Ensure all filter configurations are saved to disk on exit
        try:
            config.plugins.piconcockpit.satellite.save()
            config.plugins.piconcockpit.creator.save()
            config.plugins.piconcockpit.size.save()
            config.plugins.piconcockpit.bit.save()
            configfile.save()

        except Exception as e:
            logger.warning("Could not save configuration on exit: %s", e)

        os.popen("rm /tmp/*.png")
        self.close()

    def green(self):
        logger.info("...")
        picon_set = self["list"].getCurrent()
        logger.debug("green: picon_set = %s", picon_set)

        try:
            if picon_set:
                logger.debug("green: Processing picon_set[1] = %s", picon_set[1])

                try:
                    # Proper URL construction for picon list download
                    picon_set_url = str(picon_set[1])
                    if not picon_set_url.endswith('/'):
                        picon_set_url += '/'

                    # Construct URL using urllib.parse.urljoin for RFC 3986 compliance
                    url = urljoin(picon_set_url, str(picon_list_file))
                    logger.debug("green: Downloading picon list from URL: %s", url)

                    download_file = os.path.join(str(self.picon_dir), str(picon_list_file))
                    logger.debug("green: Saving to file: %s", download_file)

                    # Ensure URL and file path are plain strings (not bytes) for Python 3 Twisted
                    url = str(url)
                    download_file = str(download_file)

                    # Use WebRequestsAsync instead of twisted downloadPage
                    downloader = self.web_client.downloadFileAsync(url, download_file)
                    downloader.addCallback(lambda result: self.downloadPiconsCallback(result, picon_set))
                    downloader.addErrback(lambda error: self.downloadError(error, url))
                    downloader.start()

                except Exception as e:
                    logger.error("Error in green(): %s", e)
                    self.downloadError(str(e), "green")
            else:
                logger.error("green: No picon set selected")
                self.showErrorMessage(_("Please select a picon set first"))
        except Exception as e:
            logger.error("Error in green method: %s", e)

    def downloadPiconsCallback(self, result, picon_set):
        """Callback for picon list download completion"""
        logger.info("...")
        self.downloadPicons(result, picon_set)

    def downloadPicons(self, _result=None, picon_set=None):
        logger.info("...")
        logger.debug("downloadPicons: picon_set = %s", picon_set)
        if not picon_set:
            logger.error("No picon set provided")
            return

        if config.plugins.piconcockpit.all_picons.value:
            logger.info("Using all picons mode")
            picon_list_path = os.path.join(self.picon_dir, picon_list_file)
            logger.debug("downloadPicons: Reading picon list from %s", picon_list_path)

            try:
                picons = readFile(picon_list_path).splitlines()
                logger.debug("downloadPicons: Found %d picons in list", len(picons))
            except Exception as e:
                logger.error("downloadPicons: Error reading picon list: %s", e)
                self.showErrorMessage(_("Error reading picon list file"))
                return

            self.startPiconDownload(picon_set, picons)
        else:
            logger.info("Using bouquet picons mode")
            picons = self.getUserBouquetPicons()
            logger.debug("downloadPicons: Got %d bouquet picons", len(picons) if picons else 0)
            self.startPiconDownload(picon_set, picons)

    def getUserBouquetPicons(self):
        """Get user bouquet picons"""
        logger.info("...")
        picons = []

        try:
            services = self.listBouquetServices()
            logger.debug("Processing %d services", len(services))

            processed_count = 0
            for service in services:
                processed_count += 1
                # Log progress every 100 services to avoid spam but show we're working
                if processed_count % 100 == 0:
                    logger.debug("Processed %d/%d services", processed_count, len(services))

                try:
                    ref = service[0]
                    ref = ref.replace(":", "_")
                    ref = ref[:len(ref) - 1]
                    picon = ref + ".png"

                    if picon.startswith("1_"):
                        picons.append(picon)
                except Exception as e:
                    logger.error("Error processing service %s: %s", service, e)
                    continue

            return picons
        except Exception as e:
            logger.error("Error in getUserBouquetPiconsWithTimeout: %s", e)
            return []

    def listBouquetServices(self):
        """List bouquet services"""
        logger.info("...")
        try:
            tv_bouquets = getTVBouquets()
            radio_bouquets = getRadioBouquets()
            bouquets = tv_bouquets + radio_bouquets

            logger.debug("Found %d TV bouquets, %d radio bouquets, %d total", len(tv_bouquets), len(radio_bouquets), len(bouquets))

            services = []
            service_refs_seen = set()  # Avoid duplicates
            processed_bouquets = 0

            for bouquet in bouquets:
                processed_bouquets += 1
                if "Last Scanned" not in bouquet[1]:
                    try:
                        bouquet_services = getServiceList(bouquet[0])

                        # Filter out duplicates and add only new services
                        new_services = 0
                        for service in bouquet_services:
                            if service[0] not in service_refs_seen:
                                service_refs_seen.add(service[0])
                                services.append(service)
                                new_services += 1

                        logger.debug("Bouquet '%s' (%d/%d): %d new services of %d total",
                                     bouquet[1], processed_bouquets, len(bouquets),
                                     new_services, len(bouquet_services))

                    except Exception as e:
                        logger.error("Error processing bouquet %s: %s", bouquet[1], e)
                        continue
                else:
                    logger.debug("Skipping 'Last Scanned' bouquet: %s", bouquet[1])

            return services
        except Exception as e:
            logger.error("Error listing bouquet services: %s", e)
            return []

    def startPiconDownload(self, picon_set, picons):
        """Start the picon download process"""
        logger.info("...")
        logger.debug("startPiconDownload: picon_set = %s", picon_set)
        logger.debug("startPiconDownload: picons count = %d", len(picons) if picons else 0)

        if not picons:
            logger.warning("startPiconDownload: No picons to download")
            return

        # Start the picon download progress screen with correct parameters
        # picon_set[1] is the dir_url from our data structure
        self.session.open(
            PiconDownloadProgress,
            picon_set[1],   # picon_set_url
            picons,         # picons list
            self.picon_dir  # picon_dir
        )

    def downloadAllPiconsCallback(self, answer):
        """Handle callback for downloading all picons"""
        logger.info("...")
        if answer:
            try:
                # Read all picons from list file
                picons = readFile(os.path.join(self.picon_dir, picon_list_file)).splitlines()
                if picons:
                    picon_set = self["list"].getCurrent()
                    if picon_set:
                        if config.plugins.piconcockpit.delete_before_download:
                            os.popen("rm " + os.path.join(self.picon_dir, "*.png"))
                        self.session.open(PiconDownloadProgress,
                                          picon_set[1], picons, self.picon_dir)
                    else:
                        self.showErrorMessage(_("No picon set selected"))
                else:
                    self.showErrorMessage(_("No picons available for download"))
            except Exception as e:
                logger.error("Error in downloadAllPiconsCallback: %s", e)
                self.showErrorMessage(_("Error reading picon list"))

    def createList(self, fill):
        logger.info("...")
        picon_list = []
        self["preview"].hide()
        start_index = -1
        if fill:
            picon_set_list = readFile(os.path.join(
                self.picon_dir, picon_info_file)).splitlines()
            self.parseSettingsOptions(picon_set_list)

            # Debug: Check config values immediately after parseSettingsOptions

            picon_list = self.parsePiconSetList(picon_set_list)
            logger.debug("Parsed picon_list length: %d", len(picon_list))
            if picon_list:
                logger.debug("First picon item: %s", picon_list[0])
            picon_list.sort(key=lambda x: x[0])
            for i, picon_set in enumerate(picon_list):
                if picon_set[4] == self.last_picon_set:
                    logger.debug("picon_set: %s, last_picon_set: %s",
                                 picon_set[4], self.last_picon_set)
                    start_index = i
                    break
        logger.debug("Setting list with %d items", len(picon_list))
        if picon_list:
            logger.debug("Sample list item: %s", picon_list[0])
        self["list"].setList(picon_list)
        logger.debug("List count after setList: %d", self["list"].count())
        logger.debug("Current selection after setList: %s", self["list"].getCurrent())
        logger.debug("start_index: %s", start_index)
        if start_index >= 0:
            self["list"].setIndex(start_index)
            logger.debug("Current selection after setIndex: %s", self["list"].getCurrent())

    def parseSettingsOptions(self, picon_set_list):
        logger.info("...")
        size_list = {"all"}
        bit_list = {"all"}
        creator_list = {"all"}
        satellite_list = {"all"}
        for picon_set in picon_set_list:
            if not picon_set.startswith('<meta'):
                info_list = picon_set.split(';')
                if len(info_list) >= 9:
                    satellite_list.add(info_list[4])
                    creator_list.add(info_list[5])
                    bit_list.add(info_list[6].replace(
                        ' ', '').lower().replace('bit', ' bit'))
                    size_list.add(info_list[7].replace(' ', '').lower())
        if picon_set_list:
            config_init = ConfigInit()
            config_init._updateFilterChoices(list(size_list), list(bit_list),
                                             list(creator_list), list(satellite_list))

    def parsePiconSetList(self, picon_set_list):
        logger.info("...")
        logger.debug("last_picon_set: %s",
                     config.plugins.piconcockpit.last_picon_set.value)
        logger.debug("Processing %d picon set entries", len(picon_set_list))

        picon_list = []
        for picon_set in picon_set_list:
            if not picon_set.startswith('<meta'):
                info_list = picon_set.split(';')
                if len(info_list) >= 9:
                    dir_url = os.path.join(
                        config.plugins.piconcockpit.picon_server.value, info_list[0])
                    pic_url = os.path.join(
                        config.plugins.piconcockpit.picon_server.value, info_list[0], info_list[1])
                    date = info_list[2]
                    name = info_list[3]
                    satellite = info_list[4]
                    creator = info_list[5]
                    bit = (info_list[6].replace(
                        ' ', '').lower()).replace('bit', ' bit')
                    size = info_list[7].replace(' ', '').lower()
                    uploader = info_list[8]
                    identifier = str(uuid.uuid4())
                    signature = f"{satellite} | {creator} - {name} | {size} | {bit} | {uploader}"
                    display_name = f"{signature} | {date}"
                    # Apply filter configuration
                    satellite_filter = config.plugins.piconcockpit.satellite.value
                    creator_filter = config.plugins.piconcockpit.creator.value
                    size_filter = config.plugins.piconcockpit.size.value
                    bit_filter = config.plugins.piconcockpit.bit.value

                    if satellite_filter in ["all", satellite] and\
                            creator_filter in ["all", creator] and\
                            size_filter in ["all", size] and\
                            bit_filter in ["all", bit]:
                        picon_list.append(
                            (display_name, dir_url, pic_url, identifier, signature))
                    else:
                        logger.debug("Filtered out: satellite=%s (filter=%s), creator=%s (filter=%s), size=%s (filter=%s), bit=%s (filter=%s)",
                                     satellite, satellite_filter, creator, creator_filter, size, size_filter, bit, bit_filter)
        logger.debug("Returning picon_list with %d items", len(picon_list))
        return picon_list

    def downloadPreview(self):
        logger.info("...")
        self["preview"].hide()
        current = self['list'].getCurrent()
        logger.debug("downloadPreview current: %s", current)
        if current:
            logger.debug("current item details: %s", current)
            # Get URL and ensure it's properly encoded using urllib.parse
            raw_url = self['list'].getCurrent()[2]
            # Use proper URL encoding instead of simple space replacement
            url = quote(str(raw_url), safe=':/?#[]@!$&\'()*+,;=')

            picon_path = os.path.join(
                "/tmp", self['list'].getCurrent()[3] + ".png")
            if not os.path.exists(picon_path):
                try:
                    # Ensure URL and file path are plain strings (not bytes) for WebRequestsAsync
                    url = str(url)
                    picon_path = str(picon_path)

                    # Use WebRequestsAsync instead of twisted downloadPage
                    downloader = self.web_client.downloadFileAsync(url, picon_path)
                    downloader.addCallback(lambda result: self.showPreview(result, picon_path))
                    downloader.addErrback(lambda error: self.showPreview(error, picon_path))
                    downloader.start()
                except Exception as e:
                    logger.error("url: %s, e: %s", url, e)
            else:
                self.showPreview(None, picon_path)

    def showPreview(self, _result=None, path=None):
        logger.info("...")
        self["preview"].show()
        self["preview"].instance.setPixmap(LoadPixmap(path, cached=False))
