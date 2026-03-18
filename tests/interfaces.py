from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.interface import provider
from zope.schema import Choice, Date, Datetime, List, TextLine
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

list_field_opts = SimpleVocabulary(
    [
        SimpleTerm(value="fermi", title="Fermi"),
        SimpleTerm(value="einstein", title="Einstein"),
        SimpleTerm(value="bohr", title="Bohr"),
        SimpleTerm(value="heisenberg", title="Heisenberg"),
        SimpleTerm(value="hawking", title="Hawking"),
    ]
)


@provider(IFormFieldProvider)
class IMassEditTest(model.Schema):
    list_field = List(
        title="List field",
        value_type=TextLine(),
    )
    list_choice_field = List(
        title="List choice field",
        value_type=Choice(
            vocabulary=list_field_opts,
        ),
    )
    text_field = TextLine(
        title="Text field",
        required=False,
    )
    text_field_required = TextLine(title="Text field", required=True)
    date_time_field = Datetime(
        title="Datetime field",
    )
    date_field = Date(
        title="Date field",
    )
