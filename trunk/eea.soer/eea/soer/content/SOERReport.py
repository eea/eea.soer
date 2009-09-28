from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.newsitem import ATNewsItem
from eea.soer.content.interfaces import ISOERReport
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
        allowable_content_types = ('text/html',),
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
        name='soerContentType',
        required = True,
        widget=SelectionWidget(
            label='Content Type',
            label_msgid='eea.soer_label_content_types',
            description=u'Please indicate what type of content this is',
            i18n_domain='eea.soer',
            format='select',
        ),
        vocabulary=vocab.content_types,
        enforceVocabulary=True,
        index='FieldIndex:schema',
    ),

    StringField(
        name='soerCountry',
        required = False,
        mode = 'r',
        widget=SelectionWidget(
            label='Country',
            label_msgid='eea.soer_label_country',
            i18n_domain='eea.soer',
            format='select',
        ),
        vocabulary=vocab.european_countries.values(),
        enforceVocabulary=True,
    ),

    StringField(
        name='soerFeed',
        required = False,
        widget=StringWidget(
            description=u'Link to an RSS feed for this data',
            label='RSS Feed',
            label_msgid='eea.soer_label_feed',
            i18n_domain='eea.soer',
        ),
    ),

),
)

schema = getattr(ATFolder, 'schema', Schema(())).copy() + schema.copy()
schema['title'].widget.visible = 0
schema['soerCountry'].default_method = 'default_country'
schema['title'].default = 'not_set_yet'


class SOERReport(ATFolder, ATNewsItem):
    """ """
    security = ClassSecurityInfo()
    __implements__ = (getattr(ATFolder,'__implements__',()),)
    implements(ISOERReport)

    meta_type = 'SOERReport'
    portal_type = 'SOERReport'
    allowed_content_types = ['ATImage', 'Image', 'Page', 'RSSFeedRecipe', 'Link']
    _at_rename_after_creation = True

    schema = schema
    content_icon = 'document_icon.gif'

    def default_country(self):
        lang_code = self.getPhysicalPath()[-2]
        return vocab.european_countries.get(lang_code, '')
