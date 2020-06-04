import datetime

import plone.api as api
from DateTime import DateTime
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.behavior.interfaces import IBehavior
from plone.dexterity.events import EditFinishedEvent
from plone.dexterity.utils import resolveDottedName
from z3c.form.interfaces import IFieldWidget, NO_VALUE, IDataConverter
from zope.component import getMultiAdapter, getUtilitiesFor, queryUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema.interfaces import WrongType
try:
    from collective.z3cform.datagridfield.row import DictRow
except ModuleNotFoundError:
    DictRow = None

from .. import _


def get_behav(name):
    behav = queryUtility(IBehavior, name=name)
    if behav is not None:
        return behav.interface
    else:
        return resolveDottedName(name)


class MassEditForm(BrowserView):
    template = ViewPageTemplateFile('mass.pt')
    unsupported = None

    def __call__(self):
        if not self.request.form.get('form.button.Merge', '') and not self.request.form.get('form.button.Delete', ''):
            return self.template({})

        schema = self.request.get('schema', None)
        field = self.request.get('field', None)
        fkey = self.request.get('fkey', None)
        match = self.request.get('match', None)
        replacement = self.request.get('replacement_marker', None)

        if self.request.form.get('form.button.Merge', ''):
            if replacement:
                try:
                    self.replace_term(schema, field, fkey, match)
                except Exception as e:
                    api.portal.show_message(message='Failed to validate: %s' % e.__repr__(), request=self.request,
                                            type='error')
            else:
                api.portal.show_message(message='Please enter a replacement value.', request=self.request)
        elif self.request.form.get('form.button.Delete', ''):
            try:
                self.delete_term(schema, field, fkey, match)
            except Exception as e:
                api.portal.show_message(message='Failed to validate: %s' % e.__repr__(), request=self.request,
                                        type='error')

        return self.template()

    def get_schemas(self):
        """
        Our source of schemas is the object_provides KeywordIndex catalog in the catalog as well as Dexterity
        Behavior schema cache.
        :return: dotted name of interfaces
        """
        behaviors = tuple([behav[1].interface.__identifier__ for behav in getUtilitiesFor(IBehavior)])
        catalog = api.portal.get_tool('portal_catalog')
        interfaces = sorted(list(set(catalog.uniqueValuesFor('object_provides') + behaviors)),
                            key=lambda term: term.split('.')[-1])
        for interface in interfaces:
            if get_behav(interface).names():
                yield {
                    'id': interface,
                    'title': interface.split('.')[-1],
                }

    def schema_matches(self, schema):
        """
        Get a count of matches
        :param schema: dotted name interface
        :return: int
        """
        catalog = api.portal.get_tool('portal_catalog')
        if schema in catalog.uniqueValuesFor('object_provides'):
            return len(catalog(object_provides=schema))
        else:
            return 'unknown (cannot get a subset for behavior interfaces)'

    def get_fields(self):
        """
        Get all fields for a schema
        :return: fields
        """
        schema = self.request.get('schema', None)
        if not schema:
            return
        interface = get_behav(schema)
        for name in interface.names():
            if interface[name] and hasattr(interface[name], 'title'):
                yield {
                    'id': name,
                    'title': '%s [%s]' % (interface[name].title, name)
                }

    def is_dg(self):
        """
        DataGridField (collective.z3cform.datagridfield) support. Lists with dicts
        :return: bool
        """
        if not DictRow:
            return False
        schema = self.request.get('schema', None)
        field = self.request.get('field', None)
        if not field or not schema:
            return
        interface = get_behav(schema)
        return hasattr(interface[field], 'value_type') and isinstance(interface[field].value_type, DictRow)

    def get_dgschema(self):
        """ Look up the schema used for the dg field
        """
        schema = self.request.get('schema', None)
        field = self.request.get('field', None)
        if not field or not schema:
            return
        interface = get_behav(schema)
        return interface[field].value_type.schema

    def get_dgkeys(self):
        """
        Get DataGridField schema keys
        :return:
        """
        dg_schema = self.get_dgschema()
        for dg_field in dg_schema.names():
            yield {
                'id': dg_field,
                'title': dg_schema[dg_field].title,
            }

    def get_values(self):
        """
        Find all of the current values for objects that provide this schema

        :return: values
        """
        self.unsupported = None
        schema = self.request.get('schema', None)
        field = self.request.get('field', None)
        fkey = self.request.get('fkey', None)

        if self.is_dg() and not (schema and field and fkey):
            return
        elif not self.is_dg() and not (schema and field):
            return
        values = set()
        catalog = api.portal.get_tool('portal_catalog')
        if schema in catalog.uniqueValuesFor('object_provides'):
            query = catalog(object_provides=schema)
        else:
            query = catalog()
        for brain in query:
            obj = brain.getObject()
            field_value = getattr(obj, field, None)
            if not field_value:
                continue
            if field_value and isinstance(field_value, str):
                values.add(field_value)
            elif field_value and isinstance(field_value, tuple) or isinstance(field_value, list):
                for item_value in field_value:
                    if fkey:
                        if item_value[fkey] and isinstance(item_value[fkey], str):
                            values.add(item_value[fkey])
                    else:
                        if item_value and isinstance(item_value, str):
                            values.add(item_value)
            elif field_value and (isinstance(field_value, datetime.datetime) or isinstance(field_value, datetime.date)):
                values.add(field_value)
            else:
                self.unsupported = field_value.__class__.__name__
        return sorted(list(values))

    def results(self):
        """
        Find all of the content that matches the current selection

        :return: brains
        """
        schema = self.request.get('schema', None)
        field = self.request.get('field', None)
        fkey = self.request.get('fkey', None)
        match = self.request.get('match', None)
        if not schema or not field:
            return
        if self.is_dg() and not fkey:
            return
        if not match:
            return

        catalog = api.portal.get_tool('portal_catalog')
        _results = []
        if schema in catalog.uniqueValuesFor('object_provides'):
            query = catalog(object_provides=schema)
        else:
            query = catalog()
        for brain in query:
            obj = brain.getObject()
            field_value = getattr(obj, field, None)
            if field_value == match and isinstance(field_value, str):
                _results.append(brain)
            elif (isinstance(field_value, tuple) or isinstance(field_value, list)) and match in field_value:
                _results.append(brain)
            elif fkey and match in [item_value[fkey] for item_value in field_value]:
                _results.append(brain)
            elif isinstance(field_value, datetime.date) and DateTime(match).asdatetime().date() == field_value:
                _results.append(brain)
            elif isinstance(field_value, datetime.date) and DateTime(match).asdatetime() == field_value:
                _results.append(brain)
        return _results

    def replace_term(self, schema, field, fkey, match):
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
            api.portal.show_message(message=_('No replacement value given'), request=self.request, type='error')
            return

        results = self.results()
        for brain in results:
            obj = brain.getObject()
            field_value = getattr(obj, field, None)

            if isinstance(field_value, str) or \
                    isinstance(field_value, datetime.date) or isinstance(field_value, datetime.datetime):
                self.set_value(obj, schema, field, replacement)
            elif isinstance(field_value, tuple) or isinstance(field_value, list):
                if fkey:
                    for item_value in field_value:
                        if item_value[fkey] == match:
                            item_value[fkey] = replacement
                    self.set_value(obj, schema, field, field_value)
                else:
                    if replacement in field_value:
                        field_value = [item_value for item_value in field_value if item_value != match]
                    else:
                        field_value = [item_value == match and replacement or item_value for item_value in field_value]
                    self.set_value(obj, schema, field, field_value)
        api.portal.show_message(message=_('Replaced term in {} records'.format(len(results))),
                                request=self.request, type='info')

    def delete_term(self, schema, field, fkey, match):
        """
        Delete this field. For single value fields, this is set to None - it must still pass validation so
        required fields should fail.
        :param schema: dotted name schema (str)
        :param field: field
        :param fkey: boolean, representing DateGridField
        :param match: the value being matched
        :return: None
        """

        for brain in self.results():
            obj = brain.getObject()
            field_value = getattr(obj, field, None)

            if isinstance(field_value, tuple) or isinstance(field_value, list):
                if fkey:
                    for item_value in field_value:
                        if item_value[fkey] == match:
                            item_value[fkey] = None
                    # if this was the only value in the row, delete the row
                    field_value = [item_value for item_value in field_value if
                                   [i for i in list(item_value.values()) if i]]
                else:
                    field_value = [item_value for item_value in field_value if item_value != match]
                self.set_value(obj, schema, field, field_value)
            else:
                self.set_value(obj, schema, field, None)
        api.portal.show_message(message=_('Removed term in {} records'.format(len(self.results()))),
                                request=self.request, type='info')

    def set_value(self, obj, dottedname, field, field_value, attempts=0):
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
        schema = get_behav(dottedname)
        bound = schema[field].bind(obj)
        try:
            bound.validate(field_value)
        except WrongType as e:
            if attempts < attempt_limit:
                attempts += 1
                if isinstance(field_value, str):
                    field_value = str(field_value)
                    return self.set_value(obj, dottedname, field, field_value, attempts)
            else:
                api.portal.show_message(message='Failed to validate: %s' % e.__repr__(), request=self.request,
                                        type='error')
        else:
            setattr(obj, field, field_value)
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
            fkey = self.request['fkey']
            field = self.get_dgschema()[fkey]
        else:
            schema = self.request.get('schema', None)
            schema = get_behav(schema)
            field = self.request.get('field', None)
            field = schema[field]
            if hasattr(field, 'value_type'):
                field = field.value_type

        widget = getMultiAdapter((field, self.request), IFieldWidget)
        widget.name = 'replacement'
        widget.update()
        return widget


class SchemaFinderForm(BrowserView):
    def get_types(self):
        catalog = api.portal.get_tool('portal_catalog')
        return sorted(catalog.uniqueValuesFor('portal_type'))

    def schemas(self):
        content_type = self.request['content_type']
        type_info = api.portal.get_tool('portal_types').getTypeInfo(content_type)
        yield {
            'id': type_info.schema,
            'title': type_info.schema.split('.')[-1]
        }
        for behav in type_info.behaviors:
            yield {
                'id': behav,
                'title': behav.split('.')[-1]
            }
