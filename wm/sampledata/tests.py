# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import login
from plone.app.testing import SITE_OWNER_NAME
from Products.statusmessages.interfaces import IStatusMessage
from wm.sampledata import example
from wm.sampledata.testing import WM_SAMPLEDATA_INTEGRATION_TESTING
from wm.sampledata.utils import getFileContent

import os
import unittest
import wm.sampledata.tests


class FileUtilities(unittest.TestCase):
    def testPathWithModule(self):
        fc = getFileContent(wm.sampledata.tests, "example", "portlet.html")
        self.assertEqual(len(fc), 230)

    def testFileWithModule(self):
        fc = getFileContent(example, "portlet.html")
        self.assertEqual(len(fc), 230)

    def testFileWithoutModule(self):
        pkgdir = os.path.dirname(wm.sampledata.tests.__file__)
        exdir = os.path.join(pkgdir, "example")

        fc = getFileContent(None, exdir, "portlet.html")
        self.assertEqual(len(fc), 230)

    def testNoFileWithModule(self):
        self.assertRaises(IOError, getFileContent, example, "notexistent.html")


class TestView(unittest.TestCase):
    """Test @@sampledata view"""

    layer = WM_SAMPLEDATA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        # only managers can run sampledata plugins
        login(self.layer["app"], SITE_OWNER_NAME)

    def test_sampedataview(self):
        view = api.content.get_view("sampledata", self.portal, self.request)
        self.assertIsNotNone(view, "sampledata view is registered")

        plugins = [plugin["name"] for plugin in view.listPlugins()]
        self.assertIn("wm.sampledata.democontent", plugins, "view lists example plugin")

        # run the demo content plugin (set debug=True so exceptions are raised)
        view.runPlugin(u"wm.sampledata.democontent", debug=True)

        self.assertEqual(
            "successfully ran Demo Content",
            IStatusMessage(self.request).show()[1].message,
            "a status message shows the name of the plugin that has been run",
        )

        # page got published, and properly indexed
        brains = api.content.find(self.portal, SearchableText="completely")
        self.assertEqual(1, len(brains), "document text got indexed")
        self.assertEqual("published", brains[0].review_state, "document got published")


def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(FileUtilities))
    s.addTest(unittest.makeSuite(TestView))
    return s
