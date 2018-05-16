from zope.interface import Interface
from zope.schema import List, TextLine, Datetime, Date, Choice
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

list_field_opts = SimpleVocabulary([
    SimpleTerm(value='fermi', title=u'Fermi'),
    SimpleTerm(value='einstein', title=u'Einstein'),
    SimpleTerm(value='bohr', title=u'Bohr'),
    SimpleTerm(value='heisenberg', title=u'Heisenberg'),
    SimpleTerm(value='hawking', title=u'Hawking'),
])


class IMassEditTest(Interface):
    list_field = List(
        title=u'List field',
        value_type=TextLine(),
    )
    list_choice_field = List(
        title=u'List choice field',
        value_type=Choice(
            vocabulary=list_field_opts,
        )
    )
    text_field = TextLine(
        title=u'Text field',
        required=False,
    )
    text_field_required = TextLine(
        title=u'Text field',
        required=True
    )
    date_time_field = Datetime(
        title=u'Datetime field',
    )
    date_field = Date(
        title=u'Date field',
    )
