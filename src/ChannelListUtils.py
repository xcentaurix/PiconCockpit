# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0

from enigma import eServiceCenter, eServiceReference
from Components.config import config
from .Debug import logger


def getServiceList(servicetypes):
    logger.info("servicetypes: %s", servicetypes)
    service_list = []
    try:
        ref = eServiceReference(servicetypes)
        serviceHandler = eServiceCenter.getInstance()
        services = serviceHandler.list(ref)
        if services:
            while True:
                service = services.getNext()
                if not service.valid():
                    break
                info = serviceHandler.info(service)
                if info:
                    service_name = info.getName(service)
                    service_ref = service.toString()
                    if service_name and service_ref:
                        service_list.append((service_ref, service_name))
    except Exception as e:
        logger.error("Error getting service list: %s", str(e))
    return service_list


def _getBouquets(bouquet_root_str, multibouquet_aware=False):
    bouquets = []
    try:
        serviceHandler = eServiceCenter.getInstance()
        bouquet_root = eServiceReference(bouquet_root_str)
        if multibouquet_aware and not config.usage.multibouquet.value:
            info = serviceHandler.info(bouquet_root)
            if info:
                bouquets.append((bouquet_root.toString(), info.getName(bouquet_root)))
        else:
            bouquet_list = serviceHandler.list(bouquet_root)
            if bouquet_list:
                while True:
                    s = bouquet_list.getNext()
                    if not s.valid():
                        break
                    if s.flags & eServiceReference.isDirectory and not s.flags & eServiceReference.isInvisible:
                        info = serviceHandler.info(s)
                        if info:
                            bouquets.append((s.toString(), info.getName(s)))
    except Exception as e:
        logger.error("Error getting bouquets from %s: %s", bouquet_root_str, str(e))
    return bouquets


def getTVBouquets():
    logger.info("...")
    return _getBouquets('1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet', multibouquet_aware=True)


def getRadioBouquets():
    logger.info("...")
    return _getBouquets('1:7:2:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.radio" ORDER BY bouquet')
