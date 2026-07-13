# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0


from Components.config import config, ConfigText, ConfigYesNo, ConfigSelection, ConfigSubsection, ConfigNothing, NoSave
from .Debug import logger, log_levels, initLogging


server_choices = [
    ("http://picons.vuplus-support.org/", "vuplus-support.org"),
]


def _make_choices(items):
    return [("all", "all")] + [(x, x) for x in sorted(set(items)) if x != "all"]


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

        # Filter choice lists storage (persistent) - must exist before the
        # selections below so their choices can be rebuilt from cache
        # immediately, instead of starting narrow and widening afterwards.
        config.plugins.piconcockpit.cached_sizes = ConfigText(default="all", fixed_size=False, visible_width=100)
        config.plugins.piconcockpit.cached_bits = ConfigText(default="all", fixed_size=False, visible_width=100)
        config.plugins.piconcockpit.cached_creators = ConfigText(default="all", fixed_size=False, visible_width=100)
        config.plugins.piconcockpit.cached_satellites = ConfigText(default="all", fixed_size=False, visible_width=100)

        # Filter selections, choices rebuilt from cache when available
        select_all = [("all", "all")]
        config.plugins.piconcockpit.size = ConfigSelection(default="all", choices=self._cachedChoices('cached_sizes', select_all))
        config.plugins.piconcockpit.bit = ConfigSelection(default="all", choices=self._cachedChoices('cached_bits', select_all))
        config.plugins.piconcockpit.creator = ConfigSelection(default="all", choices=self._cachedChoices('cached_creators', select_all))
        config.plugins.piconcockpit.satellite = ConfigSelection(default="all", choices=self._cachedChoices('cached_satellites', select_all))

        initLogging()
        logger.debug("Configuration initialized")

    def _cachedChoices(self, cache_attr, default_choices):
        cached_val = getattr(config.plugins.piconcockpit, cache_attr).value
        if cached_val and cached_val != "all":
            return _make_choices(cached_val.split(','))
        return default_choices


def updateFilterChoices(size_list, bit_list, creator_list, satellite_list):
    for attr, cache_attr, items in (
        ('size', 'cached_sizes', size_list),
        ('bit', 'cached_bits', bit_list),
        ('creator', 'cached_creators', creator_list),
        ('satellite', 'cached_satellites', satellite_list),
    ):
        if items:
            getattr(config.plugins.piconcockpit, attr).setChoices(_make_choices(items))
            cache_element = getattr(config.plugins.piconcockpit, cache_attr)
            cache_element.value = ','.join(sorted(set(items)))
            cache_element.save()
    logger.info("Filter choices updated")
