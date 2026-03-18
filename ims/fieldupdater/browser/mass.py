import datetime

import plone.api as api
from collective.z3cform.datagridfield.row import DictRow
from DateTime import DateTime
from plone.behavior.interfaces import IBehavior
from plone.dexterity.events import EditFinishedEvent
from plone.dexterity.utils import iterSchemataForType, resolveDottedName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form.interfaces import NO_VALUE, IDataConverter, IFieldWidget
from zope.component import getMultiAdapter, queryUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import WrongType

from .. import _


def get_behav(name):
    behav = queryUtility(IBehavior, name=name)
    if behav is not None:
        return behav.interface
    else:
        return resolveDottedName(name)


def get_field_by_name(fieldname, portal_type):
    schemata = iterSchemataForType(portal_type)
    for schema in schemata:
        fields = getFieldsInOrder(schema)
        for fn, field in fields:
            if fn == fieldname:
                return field


class MassEditForm(BrowserView):
    template = ViewPageTemplateFile("mass.pt")
    unsupported = None

    def __call__(self):
        if not self.request.form.get("form.button.Merge", "") and not self.request.form.get("form.button.Delete", ""):
            return self.template({})

        portal_type = self.request.get("portal_type", None)
        field = self.request.get("field", None)
        fkey = self.request.get("fkey", None)
        match = self.request.get("match", None)
        replacement = self.request.get("replacement_marker", None)

        if self.request.form.get("form.button.Merge", ""):
            if replacement:
                try:
                    self.replace_term(portal_type, field, fkey, match)
                except Exception as e:
                    api.portal.show_message(
                        message=f"Failed to validate: {e.__repr__()}", request=self.request, type="error"
                    )
            else:
                api.portal.show_message(message="Please enter a replacement value.", request=self.request)
        elif self.request.form.get("form.button.Delete", ""):
            try:
                self.delete_term(portal_type, field, fkey, match)
            except Exception as e:
                api.portal.show_message(
                    message=f"Failed to validate: {e.__repr__()}", request=self.request, type="error"
                )

        return self.template()

    def get_types(self):
        """
        Our source of schemas is the object_provides KeywordIndex catalog in the catalog as well as Dexterity
        Behavior schema cache.
        :return: dotted name of interfaces
        """
        # behaviors = tuple([behav[1].interface.__identifier__ for behav in getUtilitiesFor(IBehavior)])
        catalog = api.portal.get_tool("portal_catalog")
        fti = api.portal.get_tool("portal_types")
        for pt in catalog.uniqueValuesFor("portal_type"):
            yield {"id": pt, "title": fti[pt].title}

    def type_matches(self, portal_type):
        """
        Get a count of matches
        :param schema: dotted name interface
        :return: int
        """
        catalog = api.portal.get_tool("portal_catalog")
        if portal_type in catalog.uniqueValuesFor("portal_type"):
            return len(catalog(portal_type=portal_type))
        else:
            return "unknown (cannot get a subset for behavior interfaces)"

    def get_fields(self):
        """
        Get all fields for a type
        :return: fields
        """
        portal_type = self.request.get("portal_type", None)
        if not portal_type:
            return

        for schema in iterSchemataForType(portal_type):
            fields = getFieldsInOrder(schema)
            for fn, field in fields:
                if getattr(field.title, "default", None):
                    yield {"id": fn, "title": f"{field.title.default} [{fn}]"}
                else:
                    yield {"id": fn, "title": f"{field.title} [{fn}]"}

    def is_dg(self) -> bool:
        """
        DataGridField (collective.z3cform.datagridfield) support. Lists with dicts
        :return: bool
        """
        portal_type = self.request.get("portal_type", None)
        field_name = self.request.get("field", None)
        if not field_name or not portal_type:
            return
        field = get_field_by_name(field_name, portal_type)
        return hasattr(field, "value_type") and isinstance(field.value_type, DictRow)

    def get_dgschema(self):
        """Look up the schema used for the dg field"""
        portal_type = self.request.get("portal_type", None)
        field = self.request.get("field", None)
        if not field or not portal_type:
            return
        return get_field_by_name(field, portal_type).value_type.schema

    def get_dgkeys(self):
        """
        Get DataGridField schema keys
        :return:
        """
        dg_schema = self.get_dgschema()
        for dg_field in dg_schema.names():
            yield {
                "id": dg_field,
                "title": dg_schema[dg_field].title,
            }

    def get_values(self):  # noqa: C901
        """
        Find all the current values for objects that provide this schema

        :return: values
        """
        self.unsupported = None
        portal_type = self.request.get("portal_type", None)
        field = self.request.get("field", None)
        fkey = self.request.get("fkey", None)

        if (self.is_dg() and not (portal_type and field and fkey)) or (
            not self.is_dg() and not (portal_type and field)
        ):
            return
        values = set()
        catalog = api.portal.get_tool("portal_catalog")
        query = catalog(portal_type=portal_type) if portal_type in catalog.uniqueValuesFor("portal_type") else catalog()

        for brain in query:
            obj = brain.getObject()
            field_value = getattr(obj, field, None)
            if not field_value:
                continue
            if field_value and isinstance(field_value, str):
                values.add(field_value)
            elif field_value and isinstance(field_value, tuple | list):
                for item_value in field_value:
                    if fkey:  # dg
                        if item_value[fkey] and isinstance(item_value[fkey], str):
                            values.add(item_value[fkey])
                    else:  # regular list or tuple
                        if item_value and isinstance(item_value, str):
                            values.add(item_value)
            elif field_value and isinstance(field_value, datetime.datetime | datetime.date):
                values.add(field_value)
            else:
                self.unsupported = field_value.__class__.__name__
        return sorted(values)

    def results(self):
        """
        Find all of the content that matches the current selection

        :return: brains
        """
        portal_type = self.request.get("portal_type", None)
        field = self.request.get("field", None)
        fkey = self.request.get("fkey", None)
        match = self.request.get("match", None)
        if not portal_type or not field:
            return
        if self.is_dg() and not fkey:
            return
        if not match:
            return

        catalog = api.portal.get_tool("portal_catalog")
        _results = []
        query = catalog(portal_type=portal_type) if portal_type in catalog.uniqueValuesFor("portal_type") else catalog()
        for brain in query:
            obj = brain.getObject()
            field_value = getattr(obj, field, None)
            checks = [
                field_value == match and isinstance(field_value, str),  # str
                isinstance(field_value, tuple | list) and match in field_value,  # iterator
                fkey and match in [item_value[fkey] for item_value in field_value],  # dg
                isinstance(field_value, datetime.date) and DateTime(match).asdatetime().date() == field_value,
                isinstance(field_value, datetime.date) and DateTime(match).asdatetime() == field_value,
            ]
            if any(checks):
                _results.append(brain)
        return _results

    def replace_term(self, portal_type: str, field: str, fkey: bool | None, match):
        """
        Replace a field term. For multi valued fields it will replace just the matching part of it. For single
        valued fields it replaces the whole field, where it matches. We get the widget from the actual schema field
        so we can use it to extract and parse the appropriate value too (!)

        :param schema: dotted name schema (str)
        :param field: field
        :param fkey: boolean, representing DateGridField
        :param match: the value being matched
        :return: None
        """
        widget = self.replacement_widget
        replacement = widget.extract()
        if replacement is not NO_VALUE:
            try:
                replacement = IDataConverter(widget).toFieldValue(replacement)
            except WrongType:
                # for some reason some things that should come in as unicode are coming in as strings
                replacement = IDataConverter(widget).toFieldValue(IDataConverter(widget).toWidgetValue(replacement))
        if not replacement or replacement is NO_VALUE:
            api.portal.show_message(message=_("No replacement value given"), request=self.request, type="error")
            return

        results = self.results()
        for brain in results:
            self.set_value_by_type(brain, portal_type, field, fkey, match, replacement)
        api.portal.show_message(
            message=_(f"Replaced term in {len(results)} records"), request=self.request, type="info"
        )

    def set_value_by_type(self, brain, portal_type: str, field: str, fkey: bool, match, replacement):
        """Set value based on field value type"""
        obj = brain.getObject()

        field_value = getattr(obj, field, None)
        if isinstance(field_value, str | datetime.date | datetime.datetime):
            self.set_value(obj, portal_type, field, replacement)
        elif isinstance(field_value, tuple | list):
            if fkey:
                for item_value in field_value:
                    if item_value[fkey] == match:
                        item_value[fkey] = replacement
                self.set_value(obj, portal_type, field, field_value)
            else:
                if replacement in field_value:
                    field_value = [item_value for item_value in field_value if item_value != match]
                else:
                    field_value = [(item_value == match and replacement) or item_value for item_value in field_value]
                self.set_value(obj, portal_type, field, field_value)

    def delete_term(self, portal_type: str, field: str, fkey: bool, match) -> None:
        for brain in self.results():
            obj = brain.getObject()
            field_value = getattr(obj, field, None)

            if isinstance(field_value, tuple | list):
                if fkey:
                    for item_value in field_value:
                        if item_value[fkey] == match:
                            item_value[fkey] = None
                    # if this was the only value in the row, delete the row
                    field_value = [
                        item_value for item_value in field_value if [i for i in list(item_value.values()) if i]
                    ]
                else:
                    field_value = [item_value for item_value in field_value if item_value != match]
                self.set_value(obj, portal_type, field, field_value)
            else:
                self.set_value(obj, portal_type, field, None)
        api.portal.show_message(
            message=_(f"Removed term in {len(self.results())} records"), request=self.request, type="info"
        )

    def set_value(self, obj, portal_type, field_name: str, field_value, attempts=0):
        """
        Set the value for an object's field. Values must be validated as defined in the schema. This can be called
        recursively as a sort of hack where zope.schema gets finicky between unicode and str.
        :param obj: the object being modified
        :param dottedname: non-resolved schema interface
        :param field: field being changed
        :param field_value: the new value of the field. In this case, for multi values, it is the entire value
        :param attempts: recursive attempts made
        :return:
        """
        attempt_limit = 1  # some of the more common validation problems are unicode where it expects ascii
        # or vice versa. Try once
        field = get_field_by_name(field_name, portal_type)
        bound = field.bind(obj)
        try:
            bound.validate(field_value)
        except WrongType as e:
            if attempts < attempt_limit:
                attempts += 1
                if isinstance(field_value, str):
                    field_value = str(field_value)
                    return self.set_value(obj, portal_type, field, field_value, attempts)
            else:
                api.portal.show_message(
                    message=f"Failed to validate: {e.__repr__()}", request=self.request, type="error"
                )
        else:
            setattr(obj, field_name, field_value)
            notify(ObjectModifiedEvent(obj))
            notify(EditFinishedEvent(obj))
            obj.reindexObject()

    @property
    def replacement_widget(self):
        """
        Get a widget for use in getting the replacement value. If the widget has a value_type, assume we want to
        render just that part. For instance, if it's a list we are only replacing one value in it so a multi value
        widget wouldn't make sense. So for schema.List(value_type=Choice()) we would render that Choice
        :return: widget
        """
        if self.is_dg():
            fkey = self.request["fkey"]
            field = self.get_dgschema()[fkey]
        else:
            portal_type = self.request.get("portal_type", None)
            field_name = self.request.get("field", None)
            field = get_field_by_name(field_name, portal_type)
            if hasattr(field, "value_type"):
                field = field.value_type

        widget = getMultiAdapter((field, self.request), IFieldWidget)
        widget.name = "replacement"
        widget.update()
        return widget
