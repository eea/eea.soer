from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.configuration import zconf
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

    TextField('text',
        required = True,
        searchable = True,
        primary = True,
        storage = AnnotationStorage(migrate=True),
        validators = ('isTidyHtmlWithCleanup',),
        #validators = ('isTidyHtml',),
        default_content_type = zconf.ATNewsItem.default_content_type,
        default_output_type = 'text/x-html-safe',
        allowable_content_types = zconf.ATNewsItem.allowed_content_types,
        widget = RichWidget(
            description = "",
            description_msgid = "help_body_text",
            label = "Body Text",
            label_msgid = "label_body_text",
            rows = 25,
            i18n_domain = "plone",
            allow_file_upload = zconf.ATDocument.allow_document_upload
        ),
    ),

    StringField(
        name='topics',
        required = True,
        widget=SelectionWidget(
            label='Topics',
            label_msgid='eea.soer_label_topics',
            i18n_domain='eea.soer',
            format='select',
        ),
        vocabulary=vocab.topics,
        enforceVocabulary=True,
    ),

    StringField(
        name='content_type',
        required = True,
        widget=SelectionWidget(
            label='Content Type',
            label_msgid='eea.soer_label_content_types',
            i18n_domain='eea.soer',
            format='select',
        ),
        vocabulary=vocab.content_types,
        enforceVocabulary=True,
    ),

    StringField(
        name='sections',
        required = True,
        widget=SelectionWidget(
            label='Content Type',
            label_msgid='eea.soer_label_sections',
            i18n_domain='eea.soer',
            format='select',
        ),
        vocabulary=vocab.sections,
        enforceVocabulary=True,
    ),

    StringField(
        name='country',
        required = True,
        widget=SelectionWidget(
            label='Country',
            label_msgid='eea.soer_label_country',
            i18n_domain='eea.soer',
            format='select',
        ),
        vocabulary=NamedVocabulary('countries'),
        enforceVocabulary=True,
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
