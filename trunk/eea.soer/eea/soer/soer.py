from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.folder import ATFolder
from eea.soer.interfaces import ISOERReport
from eea.soer.config import *
from eea.soer import vocab
from Products.ATVocabularyManager import NamedVocabulary
try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import *


schema = Schema((

    StringField(
        name='topics',
        widget=SelectionWidget(
            label='Topics',
            label_msgid='eea.soer_label_topics',
            i18n_domain='eea.soer',
            format='select',
        ),
        vocabulary=vocab.topics
    ),

    StringField(
        name='content_type',
        widget=SelectionWidget(
            label='Content Type',
            label_msgid='eea.soer_label_content_types',
            i18n_domain='eea.soer',
            format='select',
        ),
        vocabulary=vocab.content_types
    ),

    StringField(
        name='sections',
        widget=SelectionWidget(
            label='Content Type',
            label_msgid='eea.soer_label_sections',
            i18n_domain='eea.soer',
            format='select',
        ),
        vocabulary=vocab.sections
    ),

    StringField(
        name='country',
        widget=SelectionWidget(
            label='Country',
            label_msgid='eea.soer_label_country',
            i18n_domain='eea.soer',
            format='select',
        ),
        vocabulary=NamedVocabulary('countries')
    ),

),
)

schema = getattr(ATFolder, 'schema', Schema(())).copy() + schema.copy()


class SOERReport(ATFolder):
    """ """
    implements(ISOERReport)
    schema = schema
    security = ClassSecurityInfo()


registerType(SOERReport, PROJECTNAME)
