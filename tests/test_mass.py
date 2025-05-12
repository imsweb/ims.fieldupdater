import pytest
from zope.schema.interfaces import RequiredMissing

from .interfaces import IMassEditTest


class TestMassIntegration:
    def test_schemas(self, pages, view):
        assert {"id": IMassEditTest.__identifier__, "title": "IMassEditTest"} in view.get_schemas()

    def test_list_replace(self, pages, view):
        page1, page2 = pages
        page1.list_field = ["einstein", "bohr"]
        page2.list_field = ["fermi", "heisenberg"]
        match = "einstein"
        field = "list_field"
        replacement = "hawking"
        schema = IMassEditTest.__identifier__
        view.request["schema"] = schema
        view.request["field"] = field
        view.request["match"] = match
        view.request["replacement"] = replacement
        view.replace_term(schema, field, None, match)
        assert page1.list_field == ["hawking", "bohr"]
        assert page2.list_field == ["fermi", "heisenberg"]  # sanity - no change

    def test_list_delete(self, pages, view):
        page1, page2 = pages
        page1.list_field = ["einstein", "bohr"]
        page2.list_field = ["fermi", "heisenberg"]
        match = "einstein"
        field = "list_field"
        schema = IMassEditTest.__identifier__
        view.request["schema"] = schema
        view.request["field"] = field
        view.request["match"] = match
        view.delete_term(schema, field, None, match)
        assert page1.list_field == ["bohr"]
        assert page2.list_field == ["fermi", "heisenberg"]  # sanity - no change

    def test_list_replace_wrong_type(self, pages, view):
        """str converted to unicode"""
        page1, page2 = pages
        page1.list_field = ["einstein", "bohr"]
        page2.list_field = ["fermi", "heisenberg"]
        match = "einstein"
        field = "list_field"
        replacement = "hawking"
        schema = IMassEditTest.__identifier__
        view.request["schema"] = schema
        view.request["field"] = field
        view.request["match"] = match
        view.request["replacement"] = replacement
        view.replace_term(schema, field, None, match)
        assert page1.list_field == ["hawking", "bohr"]

    def test_list_choice_replace(self, pages, view):
        """A term outside of vocab will come in as NO_VALUE and result in no change"""
        page1, page2 = pages
        page1.list_choice_field = ["einstein", "bohr"]
        page2.list_choice_field = ["fermi", "heisenberg"]
        match = "einstein"
        field = "list_choice_field"
        replacement = "hawking"
        schema = IMassEditTest.__identifier__
        view.request["schema"] = schema
        view.request["field"] = field
        view.request["match"] = match
        view.request["replacement"] = replacement
        view.replace_term(schema, field, None, match)
        assert page1.list_choice_field == ["hawking", "bohr"]
        assert page2.list_choice_field == ["fermi", "heisenberg"]  # sanity - no change

    def test_list_choice_replace_invalid(self, pages, view):
        page1, page2 = pages
        page1.list_choice_field = ["einstein", "bohr"]
        page2.list_choice_field = ["fermi", "heisenberg"]
        match = "einstein"
        field = "list_choice_field"
        replacement = "dirac"
        schema = IMassEditTest.__identifier__
        view.request["schema"] = schema
        view.request["field"] = field
        view.request["match"] = match
        view.request["replacement"] = replacement
        view.replace_term(schema, field, None, match)
        assert "dirac" not in page1.list_choice_field

    def test_textline_replace(self, pages, view):
        page1, page2 = pages
        page1.text_field = "einstein"
        match = "einstein"
        field = "text_field"
        replacement = "hawking"
        schema = IMassEditTest.__identifier__
        view.request["schema"] = schema
        view.request["field"] = field
        view.request["match"] = match
        view.request["replacement"] = replacement
        view.replace_term(schema, field, None, match)
        assert page1.text_field == "hawking"

    def test_textline_delete(self, pages, view):
        page1, page2 = pages
        page1.text_field = "einstein"
        match = "einstein"
        field = "text_field"
        schema = IMassEditTest.__identifier__
        view.request["schema"] = schema
        view.request["field"] = field
        view.request["match"] = match
        view.delete_term(schema, field, None, match)
        assert page1.text_field is None

    def test_textline_delete_required(self, pages, view):
        page1, page2 = pages
        page1.text_field_required = "einstein"
        match = "einstein"
        field = "text_field_required"
        schema = IMassEditTest.__identifier__
        view.request["schema"] = schema
        view.request["field"] = field
        view.request["match"] = match
        with pytest.raises(RequiredMissing):
            view.delete_term(schema, field, None, match)

    def test_unicode_conversion(self, pages, view):
        """The widget should really handle this, but we do have this as a failsafe"""
        page1, page2 = pages
        page1.text_field = "einstein"
        match = "einstein"
        field = "text_field"
        replacement = "hawking"
        schema = IMassEditTest.__identifier__
        view.request["schema"] = schema
        view.request["field"] = field
        view.request["match"] = match
        view.request["replacement"] = replacement
        view.replace_term(schema, field, None, match)
        assert page1.text_field == "hawking"
        assert isinstance(page1.text_field, str)
