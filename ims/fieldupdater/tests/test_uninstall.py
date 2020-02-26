from Products.CMFPlone.utils import get_installer
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from . import base
from .. import testing


class TestUninstall(base.IntegrationTestCase):
    layer = testing.INTEGRATION

    def setUp(self):
        self.portal = self.layer['portal']
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer = get_installer(self.portal)
        self.installer.uninstall_product('ims.fieldupdater')
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if ims.contacts is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed('ims.fieldupdater'))
