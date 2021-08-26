# -*- coding: utf-8 -*-
from wm.sampledata.interfaces import ISampleDataPlugin
from zope.component import getUtility
from zope.interface import implementer

import logging


logger = logging.getLogger("wm.sampledata")


@implementer(ISampleDataPlugin)
class PluginGroup(object):
    """useful baseclass for grouping plugins by their name"""

    PLUGINS = []

    def generate(self, context):
        for plugin in self.PLUGINS:
            if isinstance(plugin, str):
                plugin = getUtility(ISampleDataPlugin, name=plugin)
                plugin.generate(context)
            else:
                plugin().generate(context)
