import base
from zope.schema.interfaces import WrongType, WrongContainedType, RequiredMissing

from .interfaces import IMassEditTest


class TestMassIntegration(base.IntegrationTestCase):
    def test_schemas(self):
        self.assertIn({'id': IMassEditTest.__identifier__, 'title': 'IMassEditTest'}, self.view.get_schemas())

    def test_list_replace(self):
        self.page1.list_field = [u'einstein', u'bohr']
        self.page2.list_field = [u'fermi', u'heisenberg']
        match = u'einstein'
        field = 'list_field'
        replacement = u'hawking'
        schema = IMassEditTest.__identifier__
        self.view.request['schema'] = schema
        self.view.request['field'] = field
        self.view.request['match'] = match
        self.view.request['replacement'] = replacement
        self.view.replace_term(schema, field, None, match)
        self.assertEquals(self.page1.list_field, [u'hawking', u'bohr'])
        self.assertEquals(self.page2.list_field, [u'fermi', u'heisenberg'])  # sanity - no change

    def test_list_delete(self):
        self.page1.list_field = [u'einstein', u'bohr']
        self.page2.list_field = [u'fermi', u'heisenberg']
        match = u'einstein'
        field = 'list_field'
        schema = IMassEditTest.__identifier__
        self.view.request['schema'] = schema
        self.view.request['field'] = field
        self.view.request['match'] = match
        self.view.delete_term(schema, field, None, match)
        self.assertEquals(self.page1.list_field, [u'bohr'])
        self.assertEquals(self.page2.list_field, [u'fermi', u'heisenberg'])  # sanity - no change

    def test_list_replace_wrong_type(self):
        self.page1.list_field = [u'einstein', u'bohr']
        self.page2.list_field = [u'fermi', u'heisenberg']
        match = u'einstein'
        field = 'list_field'
        replacement = 'hawking'
        schema = IMassEditTest.__identifier__
        self.view.request['schema'] = schema
        self.view.request['field'] = field
        self.view.request['match'] = match
        self.view.request['replacement'] = replacement
        self.assertRaises(WrongType, self.view.replace_term, schema, field, None, match)

    def test_list_choice_replace(self):
        self.page1.list_choice_field = [u'einstein', u'bohr']
        self.page2.list_choice_field = [u'fermi', u'heisenberg']
        match = u'einstein'
        field = 'list_choice_field'
        replacement = u'hawking'
        schema = IMassEditTest.__identifier__
        self.view.request['schema'] = schema
        self.view.request['field'] = field
        self.view.request['match'] = match
        self.view.request['replacement'] = replacement
        self.view.replace_term(schema, field, None, match)
        self.assertEquals(self.page1.list_choice_field, [u'hawking', u'bohr'])
        self.assertEquals(self.page2.list_choice_field, [u'fermi', u'heisenberg'])  # sanity - no change

    def test_list_choice_replace_invalid(self):
        self.page1.list_choice_field = [u'einstein', u'bohr']
        self.page2.list_choice_field = [u'fermi', u'heisenberg']
        match = u'einstein'
        field = 'list_choice_field'
        replacement = u'dirac'
        schema = IMassEditTest.__identifier__
        self.view.request['schema'] = schema
        self.view.request['field'] = field
        self.view.request['match'] = match
        self.view.request['replacement'] = replacement
        self.assertRaises(WrongContainedType, self.view.replace_term, schema, field, None, match)

    def test_textline_replace(self):
        self.page1.text_field = u'einstein'
        match = u'einstein'
        field = 'text_field'
        replacement = u'hawking'
        schema = IMassEditTest.__identifier__
        self.view.request['schema'] = schema
        self.view.request['field'] = field
        self.view.request['match'] = match
        self.view.request['replacement'] = replacement
        self.view.replace_term(schema, field, None, match)
        self.assertEquals(self.page1.text_field, u'hawking')

    def test_textline_delete(self):
        self.page1.text_field = u'einstein'
        match = u'einstein'
        field = 'text_field'
        schema = IMassEditTest.__identifier__
        self.view.request['schema'] = schema
        self.view.request['field'] = field
        self.view.request['match'] = match
        self.view.delete_term(schema, field, None, match)
        self.assertEquals(self.page1.text_field, None)

    def test_textline_delete_required(self):
        self.page1.text_field_required = u'einstein'
        match = u'einstein'
        field = 'text_field_required'
        schema = IMassEditTest.__identifier__
        self.view.request['schema'] = schema
        self.view.request['field'] = field
        self.view.request['match'] = match
        self.assertRaises(RequiredMissing, self.view.delete_term, schema, field, None, match)

    def test_unicode_conversion(self):
        """ The widget should really handle this, but we do have this as a failsafe """
        self.page1.text_field = u'einstein'
        match = u'einstein'
        field = 'text_field'
        replacement = 'hawking'
        schema = IMassEditTest.__identifier__
        self.view.request['schema'] = schema
        self.view.request['field'] = field
        self.view.request['match'] = match
        self.view.request['replacement'] = replacement
        self.assertRaises(WrongType, self.view.replace_term, schema, field, None, match)


def test_suite():
    import unittest
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
