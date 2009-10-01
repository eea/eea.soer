from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.newsitem import ATNewsItem
from eea.soer.content.interfaces import ISOERReport
from eea.soer.config import *
from eea.soer import vocab
from Products.ATVocabularyManager import NamedVocabulary
from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
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
        vocabulary=NamedVocabulary('eea.soer.vocab.content_types'),
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
        vocabulary=NamedVocabulary('eea.soer.vocab.european_countries'),
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

    def getTermTitle(self, vocab_name, term_key):
        """Utility method to get the title form a vocabulary term"""
        portal = getToolByName(self, 'portal_url').getPortalObject()
        atvm = getToolByName(portal, ATVOCABULARYTOOL, None)
        vocab = atvm.getVocabularyByName(vocab_name)
        term = getattr(vocab, term_key, None)
        if term == None:
            return ''
        return term.title;

    def getSoerContentTypeName(self):
        return self.getTermTitle('eea.soer.vocab.content_types', self.getSoerContentType())

    def getSoerCountryName(self):
        return self.getTermTitle('eea.soer.vocab.european_countries', self.getSoerCountry())

    def default_country(self):
        path = self.getPhysicalPath()
        if len(path) >= 2:
            country_code = path[-2]
            return country_code
        return ''
