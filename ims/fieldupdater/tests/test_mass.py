from zope.schema.interfaces import RequiredMissing

from . import base
from .interfaces import IMassEditTest


class TestMassIntegration(base.IntegrationTestCase):
    def test_schemas(self):
        self.assertIn({'id': IMassEditTest.__identifier__, 'title': 'IMassEditTest'}, self.view.get_schemas())

    def test_list_replace(self):
        self.page1.list_field = ['einstein', 'bohr']
        self.page2.list_field = ['fermi', 'heisenberg']
        match = 'einstein'
        field = 'list_field'
        replacement = 'hawking'
        schema = IMassEditTest.__identifier__
        self.view.request['schema'] = schema
        self.view.request['field'] = field
        self.view.request['match'] = match
        self.view.request['replacement'] = replacement
        self.view.replace_term(schema, field, None, match)
        self.assertEqual(self.page1.list_field, ['hawking', 'bohr'])
        self.assertEqual(self.page2.list_field, ['fermi', 'heisenberg'])  # sanity - no change

    def test_list_delete(self):
        self.page1.list_field = ['einstein', 'bohr']
        self.page2.list_field = ['fermi', 'heisenberg']
        match = 'einstein'
        field = 'list_field'
        schema = IMassEditTest.__identifier__
        self.view.request['schema'] = schema
        self.view.request['field'] = field
        self.view.request['match'] = match
        self.view.delete_term(schema, field, None, match)
        self.assertEqual(self.page1.list_field, ['bohr'])
        self.assertEqual(self.page2.list_field, ['fermi', 'heisenberg'])  # sanity - no change

    def test_list_replace_wrong_type(self):
        """ str converted to unicode """
        self.page1.list_field = ['einstein', 'bohr']
        self.page2.list_field = ['fermi', 'heisenberg']
        match = 'einstein'
        field = 'list_field'
        replacement = 'hawking'
        schema = IMassEditTest.__identifier__
        self.view.request['schema'] = schema
        self.view.request['field'] = field
        self.view.request['match'] = match
        self.view.request['replacement'] = replacement
        self.view.replace_term(schema, field, None, match)
        self.assertEqual(self.page1.list_field, ['hawking', 'bohr'])

    def test_list_choice_replace(self):
        """ A term outside of vocab will come in as NO_VALUE and result in no change """
        self.page1.list_choice_field = ['einstein', 'bohr']
        self.page2.list_choice_field = ['fermi', 'heisenberg']
        match = 'einstein'
        field = 'list_choice_field'
        replacement = 'hawking'
        schema = IMassEditTest.__identifier__
        self.view.request['schema'] = schema
        self.view.request['field'] = field
        self.view.request['match'] = match
        self.view.request['replacement'] = replacement
        self.view.replace_term(schema, field, None, match)
        self.assertEqual(self.page1.list_choice_field, ['hawking', 'bohr'])
        self.assertEqual(self.page2.list_choice_field, ['fermi', 'heisenberg'])  # sanity - no change

    def test_list_choice_replace_invalid(self):
        self.page1.list_choice_field = ['einstein', 'bohr']
        self.page2.list_choice_field = ['fermi', 'heisenberg']
        match = 'einstein'
        field = 'list_choice_field'
        replacement = 'dirac'
        schema = IMassEditTest.__identifier__
        self.view.request['schema'] = schema
        self.view.request['field'] = field
        self.view.request['match'] = match
        self.view.request['replacement'] = replacement
        self.view.replace_term(schema, field, None, match)
        self.assertNotIn('dirac', self.page1.list_choice_field)

    def test_textline_replace(self):
        self.page1.text_field = 'einstein'
        match = 'einstein'
        field = 'text_field'
        replacement = 'hawking'
        schema = IMassEditTest.__identifier__
        self.view.request['schema'] = schema
        self.view.request['field'] = field
        self.view.request['match'] = match
        self.view.request['replacement'] = replacement
        self.view.replace_term(schema, field, None, match)
        self.assertEqual(self.page1.text_field, 'hawking')

    def test_textline_delete(self):
        self.page1.text_field = 'einstein'
        match = 'einstein'
        field = 'text_field'
        schema = IMassEditTest.__identifier__
        self.view.request['schema'] = schema
        self.view.request['field'] = field
        self.view.request['match'] = match
        self.view.delete_term(schema, field, None, match)
        self.assertEqual(self.page1.text_field, None)

    def test_textline_delete_required(self):
        self.page1.text_field_required = 'einstein'
        match = 'einstein'
        field = 'text_field_required'
        schema = IMassEditTest.__identifier__
        self.view.request['schema'] = schema
        self.view.request['field'] = field
        self.view.request['match'] = match
        self.assertRaises(RequiredMissing, self.view.delete_term, schema, field, None, match)

    def test_unicode_conversion(self):
        """ The widget should really handle this, but we do have this as a failsafe """
        self.page1.text_field = 'einstein'
        match = 'einstein'
        field = 'text_field'
        replacement = 'hawking'
        schema = IMassEditTest.__identifier__
        self.view.request['schema'] = schema
        self.view.request['field'] = field
        self.view.request['match'] = match
        self.view.request['replacement'] = replacement
        self.view.replace_term(schema, field, None, match)
        self.assertEqual(self.page1.text_field, 'hawking')
        self.assertIsInstance(self.page1.text_field, str)


class TestMassFunctional(base.FunctionalTestCase):
    def test_mass_edit(self):
        self.page1.list_choice_field = 'einstein'
        self.browser.open(
            self.portal.absolute_url() + '/@@mass-edit?schema=' + IMassEditTest.__identifier__ + '&field=list_choice_field&match=')
        # ctrl = self.browser.getControl
        # ctrl(name='form.buttons.search').click()


def test_suite():
    import unittest
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
