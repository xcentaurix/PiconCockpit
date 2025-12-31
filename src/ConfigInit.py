# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.config import config, ConfigText, ConfigYesNo, ConfigSelection, ConfigSubsection, ConfigNothing, NoSave, configfile
from .Debug import logger, log_levels, initLogging


server_choices = [
    ("http://picons.vuplus-support.org/", "vuplus-support.org"),
]


class ConfigInit():

    def __init__(self):
        """Initialize configuration with default values"""
        config.plugins.piconcockpit = ConfigSubsection()
        config.plugins.piconcockpit.fake_entry = NoSave(ConfigNothing())

        # Server and directory settings
        config.plugins.piconcockpit.picon_server = ConfigSelection(
            default=server_choices[0][0], choices=server_choices)
        config.plugins.piconcockpit.picon_directory = ConfigText(
            default="/usr/share/enigma2/picon", fixed_size=False, visible_width=50)

        # Download behavior settings
        config.plugins.piconcockpit.all_picons = ConfigYesNo(default=False)
        config.plugins.piconcockpit.delete_before_download = ConfigYesNo(default=False)
        config.plugins.piconcockpit.last_picon_set = ConfigText(
            default="", fixed_size=False, visible_width=20)

        # Debug settings
        config.plugins.piconcockpit.debug_log_level = ConfigSelection(
            default="INFO", choices=list(log_levels.keys()))

        # Filter choice lists storage (persistent)
        config.plugins.piconcockpit.cached_sizes = ConfigText(default="all", fixed_size=False, visible_width=100)
        config.plugins.piconcockpit.cached_bits = ConfigText(default="all", fixed_size=False, visible_width=100)
        config.plugins.piconcockpit.cached_creators = ConfigText(default="all", fixed_size=False, visible_width=100)
        config.plugins.piconcockpit.cached_satellites = ConfigText(default="all", fixed_size=False, visible_width=100)

        # Filter selections with default "all" only
        select_all = [("all", "all")]
        config.plugins.piconcockpit.size = ConfigSelection(default="all", choices=select_all)
        config.plugins.piconcockpit.bit = ConfigSelection(default="all", choices=select_all)
        config.plugins.piconcockpit.creator = ConfigSelection(default="all", choices=select_all)
        config.plugins.piconcockpit.satellite = ConfigSelection(default="all", choices=select_all)

        # Load cached choices if available
        self._loadCachedChoices()

        initLogging()
        logger.debug("Configuration initialized")

    def _loadCachedChoices(self):
        """Load cached filter choices from persistent storage"""
        def parse_choices(cached_text):
            if not cached_text or cached_text == "all":
                return [("all", "all")]
            items = cached_text.split(',')
            return [("all", "all")] + [(x, x) for x in sorted(set(items)) if x != "all"]

        # Recreate ConfigSelection objects with cached choices if they exist
        if hasattr(config.plugins.piconcockpit, 'cached_sizes') and config.plugins.piconcockpit.cached_sizes.value != "all":
            current_value = config.plugins.piconcockpit.size.value
            new_choices = parse_choices(config.plugins.piconcockpit.cached_sizes.value)
            config.plugins.piconcockpit.size = ConfigSelection(default=current_value, choices=new_choices)
        if hasattr(config.plugins.piconcockpit, 'cached_bits') and config.plugins.piconcockpit.cached_bits.value != "all":
            current_value = config.plugins.piconcockpit.bit.value
            new_choices = parse_choices(config.plugins.piconcockpit.cached_bits.value)
            config.plugins.piconcockpit.bit = ConfigSelection(default=current_value, choices=new_choices)
        if hasattr(config.plugins.piconcockpit, 'cached_creators') and config.plugins.piconcockpit.cached_creators.value != "all":
            current_value = config.plugins.piconcockpit.creator.value
            new_choices = parse_choices(config.plugins.piconcockpit.cached_creators.value)
            config.plugins.piconcockpit.creator = ConfigSelection(default=current_value, choices=new_choices)
        if hasattr(config.plugins.piconcockpit, 'cached_satellites') and config.plugins.piconcockpit.cached_satellites.value != "all":
            current_value = config.plugins.piconcockpit.satellite.value
            new_choices = parse_choices(config.plugins.piconcockpit.cached_satellites.value)
            config.plugins.piconcockpit.satellite = ConfigSelection(default=current_value, choices=new_choices)

    def _updateFilterChoices(self, size_list, bit_list, creator_list, satellite_list):
        """Update filter choices with new data from server and save to persistent storage"""
        def make_choices(items):
            if not items:
                return [("all", "all")]
            return [("all", "all")] + [(x, x) for x in sorted(set(items)) if x != "all"]

        # Create new ConfigSelection objects instead of modifying existing ones
        if size_list:
            logger.debug("Recreating size config, old type: %s", type(config.plugins.piconcockpit.size))
            current_value = config.plugins.piconcockpit.size.value
            new_choices = make_choices(size_list)
            config.plugins.piconcockpit.size = ConfigSelection(default=current_value, choices=new_choices)
            config.plugins.piconcockpit.cached_sizes.value = ','.join(sorted(set(size_list)))
            logger.debug("New size config type: %s", type(config.plugins.piconcockpit.size))
        if bit_list:
            current_value = config.plugins.piconcockpit.bit.value
            new_choices = make_choices(bit_list)
            config.plugins.piconcockpit.bit = ConfigSelection(default=current_value, choices=new_choices)
            config.plugins.piconcockpit.cached_bits.value = ','.join(sorted(set(bit_list)))
        if creator_list:
            current_value = config.plugins.piconcockpit.creator.value
            new_choices = make_choices(creator_list)
            config.plugins.piconcockpit.creator = ConfigSelection(default=current_value, choices=new_choices)
            config.plugins.piconcockpit.cached_creators.value = ','.join(sorted(set(creator_list)))
        if satellite_list:
            current_value = config.plugins.piconcockpit.satellite.value
            new_choices = make_choices(satellite_list)
            config.plugins.piconcockpit.satellite = ConfigSelection(default=current_value, choices=new_choices)
            config.plugins.piconcockpit.cached_satellites.value = ','.join(sorted(set(satellite_list)))

        # Save to persistent storage
        configfile.save()
        logger.info("Filter choices updated and cached")
