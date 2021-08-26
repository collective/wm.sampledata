# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope.interface.interface import Attribute


class ISampleDataPlugin(Interface):

    """ """

    title = Attribute("Plugin Title")

    description = Attribute("Describes what is being generated")

    def generate(context):
        """Generate sample data of this plugin."""

        pass
