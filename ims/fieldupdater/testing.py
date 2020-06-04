import ims.fieldupdater
from plone.app.testing import PloneSandboxLayer, IntegrationTesting, FunctionalTesting, applyProfile, PLONE_FIXTURE

has_dgf = True
try:
    import collective.z3cform.datagridfield
except ImportError:
    has_dgf = False


class FieldUpdaterSiteLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configuration_context):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        if has_dgf:
            self.loadZCML(package=collective.z3cform.datagridfield)
        self.loadZCML(package=ims.fieldupdater)

    def setUpPloneSite(self, portal):
        if has_dgf:
            applyProfile(portal, 'collective.z3cform.datagridfield:default')
        applyProfile(portal, 'ims.fieldupdater:default')


FIELD_UPDATER_SITE_FIXTURE = FieldUpdaterSiteLayer()

INTEGRATION = IntegrationTesting(
    bases=(FIELD_UPDATER_SITE_FIXTURE,),
    name="ims.fieldupdater:Integration"
)

FUNCTIONAL = FunctionalTesting(
    bases=(FIELD_UPDATER_SITE_FIXTURE,),
    name="ims.fieldupdater:Functional"
)
