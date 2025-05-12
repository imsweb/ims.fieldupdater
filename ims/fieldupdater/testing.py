from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.protect import auto
from plone.testing.zope import WSGI_SERVER_FIXTURE

import ims.fieldupdater

ORIGINAL_CSRF_DISABLED = auto.CSRF_DISABLED


class FieldUpdaterLayer(PloneSandboxLayer):
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        auto.CSRF_DISABLED = True
        self.loadZCML(package=ims.fieldupdater)

    def tearDownZope(self, app):
        auto.CSRF_DISABLED = ORIGINAL_CSRF_DISABLED

    def setUpPloneSite(self, portal):
        applyProfile(portal, "ims.fieldupdater:default")


FIXTURE = FieldUpdaterLayer()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name="FieldUpdaterLayer:IntegrationTesting",
)

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, WSGI_SERVER_FIXTURE),
    name="FieldUpdaterLayer:FunctionalTesting",
)

RESTAPI_TESTING = FunctionalTesting(
    bases=(FIXTURE, WSGI_SERVER_FIXTURE),
    name="FieldUpdaterLayer:RestAPITesting",
)

ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        WSGI_SERVER_FIXTURE,
    ),
    name="FieldUpdaterLayer:AcceptanceTesting",
)
