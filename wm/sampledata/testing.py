# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import wm.sampledata


class SampledataLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import wm.sampledata.example

        self.loadZCML(package=wm.sampledata)
        self.loadZCML(package=wm.sampledata.example)


WM_SAMPLEDATA_FIXTURE = SampledataLayer()


WM_SAMPLEDATA_INTEGRATION_TESTING = IntegrationTesting(
    bases=(WM_SAMPLEDATA_FIXTURE,),
    name="SampledataLayer:IntegrationTesting",
)


WM_SAMPLEDATA_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(WM_SAMPLEDATA_FIXTURE,),
    name="SampledataLayer:FunctionalTesting",
)


