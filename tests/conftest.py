import pytest
from ims.fieldupdater.testing import FUNCTIONAL_TESTING
from ims.fieldupdater.testing import INTEGRATION_TESTING
from plone import api
from pytest_plone import fixtures_factory
from zope.interface.declarations import directlyProvides

from .interfaces import IMassEditTest

try:
    from Products.CMFCore.indexing import processQueue
except ImportError:

    def processQueue():
        pass


pytest_plugins = ["pytest_plone"]

globals().update(
    fixtures_factory((
        (FUNCTIONAL_TESTING, "functional"),
        (INTEGRATION_TESTING, "integration"),
    ))
)


@pytest.fixture
def pages(portal):
    docs = []
    with api.env.adopt_roles(["Manager"]):
        for idx in range(1, 3):
            doc = api.content.create(container=portal, type="Document", id=f"page{idx}", title=f"Page{idx}")
            directlyProvides(doc, IMassEditTest)
            docs.append(doc)
    processQueue()
    return docs


@pytest.fixture
def view(portal):
    return api.content.get_view(context=portal, name="mass-edit")
