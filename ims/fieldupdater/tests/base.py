import unittest

import transaction
from plone.app.testing import setRoles, TEST_USER_ID, SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.testing.zope import Browser
from zope.interface.declarations import directlyProvides

from .interfaces import IMassEditTest
from .. import testing

try:
    from Products.CMFCore.indexing import processQueue
except ImportError:
    def processQueue():
        pass


class UnitTestCase(unittest.TestCase):
    def setUp(self):
        pass


class IntegrationTestCase(unittest.TestCase):
    layer = testing.INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']
        self.request = self.layer
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.view = self.portal.restrictedTraverse('@@mass-edit')
        self.portal.invokeFactory('Document', 'page1')
        self.portal.invokeFactory('Document', 'page2')

        self.page1 = self.portal['page1']
        self.page2 = self.portal['page2']
        directlyProvides(self.page1, IMassEditTest)
        directlyProvides(self.page2, IMassEditTest)
        self.page1.reindexObject()
        self.page2.reindexObject()
        processQueue()


class FunctionalTestCase(IntegrationTestCase):
    layer = testing.FUNCTIONAL

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )
        transaction.commit()
