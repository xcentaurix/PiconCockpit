# coding=utf-8
#
# Copyright (C) 2018-2026 by xcentaurix
#
# Compatibility layer for standard Enigma2 to replace DreamOS APIs.ServiceData
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from enigma import eServiceCenter, eServiceReference
from ServiceReference import ServiceReference
from .Debug import logger


def getServiceList(bouquet_ref):
    """
    Get list of services from a bouquet reference.
    Returns list of tuples: (service_reference_string, service_name)
    """
    services = []

    try:
        if isinstance(bouquet_ref, str):
            bouquet_ref = eServiceReference(bouquet_ref)
        elif isinstance(bouquet_ref, tuple) and len(bouquet_ref) > 0:
            bouquet_ref = eServiceReference(bouquet_ref[0])

        service_center = eServiceCenter.getInstance()
        service_list = service_center.list(bouquet_ref)

        if service_list:
            count = 0
            max_services = 10000  # Prevent infinite loops

            while count < max_services:
                service_ref = service_list.getNext()
                if not service_ref.valid():
                    break

                count += 1
                service_ref_str = service_ref.toString()

                # Skip markers and other non-service entries
                if service_ref.flags & eServiceReference.isMarker:
                    continue

                # Skip invalid service references
                if not service_ref_str or service_ref_str == "":
                    continue

                # Get service name safely
                try:
                    info = service_center.info(service_ref)
                    if info:
                        service_name = info.getName(service_ref) or ""
                    else:
                        service_name = ServiceReference(service_ref).getServiceName()
                except Exception:
                    service_name = ""

                services.append((service_ref_str, service_name))

            if count >= max_services:
                # Log warning but don't fail completely
                pass

    except Exception:
        # Return empty list on error but don't crash
        pass

    return services


def getTVBouquets():
    """
    Get list of TV bouquets.
    Returns list of tuples: (bouquet_reference_string, bouquet_name)
    """
    bouquets = []

    try:
        # Correct TV bouquets root reference - use the standard bouquets.tv reference
        tv_root = eServiceReference('1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet')

        service_center = eServiceCenter.getInstance()
        bouquet_list = service_center.list(tv_root)

        # Debug: Check if bouquet_list is valid
        logger.debug("ServiceDataCompat: getTVBouquets - bouquet_list is valid: %s", bouquet_list is not None)

        if bouquet_list:
            count = 0
            max_bouquets = 100  # Realistic limit for actual bouquets

            while count < max_bouquets:
                bouquet_ref = bouquet_list.getNext()
                if not bouquet_ref.valid():
                    break

                count += 1
                bouquet_ref_str = bouquet_ref.toString()

                # Debug: Log what we find
                logger.debug("ServiceDataCompat: Found bouquet ref: %s", bouquet_ref_str[:100])

                # Skip invalid bouquet references
                if not bouquet_ref_str or bouquet_ref_str == "":
                    logger.debug("ServiceDataCompat: Skipping empty bouquet ref")
                    continue

                # Only process actual bouquet references (should start with 1:7:1 for TV bouquets)
                if not bouquet_ref_str.startswith('1:7:1:'):
                    logger.debug("ServiceDataCompat: Skipping non-bouquet ref: %s", bouquet_ref_str[:50])
                    continue

                # Get bouquet name safely
                try:
                    info = service_center.info(bouquet_ref)
                    if info:
                        bouquet_name = info.getName(bouquet_ref) or ""
                    else:
                        bouquet_name = ServiceReference(bouquet_ref).getServiceName()

                    # Skip empty or invalid names
                    if not bouquet_name or bouquet_name.strip() == "":
                        continue

                except Exception:
                    bouquet_name = ""
                    continue

                bouquets.append((bouquet_ref_str, bouquet_name))
                logger.debug("ServiceDataCompat: Added TV bouquet: %s", bouquet_name)

    except Exception as e:
        # Log the error for debugging
        logger.error("ServiceDataCompat: Error in getTVBouquets: %s", e)

    logger.debug("ServiceDataCompat: getTVBouquets returning %d bouquets", len(bouquets))
    return bouquets


def getRadioBouquets():
    """
    Get list of Radio bouquets.
    Returns list of tuples: (bouquet_reference_string, bouquet_name)
    """
    bouquets = []

    try:
        # Correct radio bouquets root reference
        radio_root = eServiceReference('1:7:2:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.radio" ORDER BY bouquet')

        service_center = eServiceCenter.getInstance()
        bouquet_list = service_center.list(radio_root)

        if bouquet_list:
            count = 0
            max_bouquets = 50  # Realistic limit for radio bouquets

            while count < max_bouquets:
                bouquet_ref = bouquet_list.getNext()
                if not bouquet_ref.valid():
                    break

                count += 1
                bouquet_ref_str = bouquet_ref.toString()

                # Skip invalid bouquet references
                if not bouquet_ref_str or bouquet_ref_str == "":
                    continue

                # Only process actual bouquet references (should start with 1:7:2)
                if not bouquet_ref_str.startswith('1:7:2:'):
                    continue

                # Get bouquet name safely
                try:
                    info = service_center.info(bouquet_ref)
                    if info:
                        bouquet_name = info.getName(bouquet_ref) or ""
                    else:
                        bouquet_name = ServiceReference(bouquet_ref).getServiceName()

                    # Skip empty or invalid names
                    if not bouquet_name or bouquet_name.strip() == "":
                        continue

                except Exception:
                    bouquet_name = ""
                    continue

                bouquets.append((bouquet_ref_str, bouquet_name))

    except Exception:
        # Return empty list on error but don't crash
        pass

    return bouquets
