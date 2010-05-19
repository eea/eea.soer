from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.newsitem import ATNewsItem
from eea.soer.content.interfaces import ISOERReport
from eea.soer.config import *
from Products.ATVocabularyManager import NamedVocabulary
from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
from Products.CMFPlone.PloneBatch import Batch
try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import *

schema = Schema((
  
    #keyMessage
    TextField('keyMessage',
        required = False,
        searchable = True,
        primary = False,
        storage = AnnotationStorage(migrate=True),
        validators = ('isTidyHtmlWithCleanup',),
        default_content_type = zconf.ATNewsItem.default_content_type,
        default_output_type = 'text/x-html-safe',
        allowable_content_types = ('text/html',),
        widget = RichWidget(
            description = "",
            description_msgid = "help_body_text",
            label = "Key message",
            label_msgid = "label_body_text",
            rows = 5,
            i18n_domain = "plone",
            allow_file_upload = False,
        ),
    ),

    #assesment
    TextField('text',
        required = True,
        searchable = True,
        primary = True,
        storage = AnnotationStorage(migrate=True),
        validators = ('isTidyHtmlWithCleanup',),
        default_content_type = zconf.ATNewsItem.default_content_type,
        default_output_type = 'text/x-html-safe',
        allowable_content_types = ('text/html',),
        widget = RichWidget(
            description = "",
            description_msgid = "help_body_text",
            label = "Assessment",
            label_msgid = "label_body_text",
            rows = 25,
            i18n_domain = "plone",
            allow_file_upload = zconf.ATDocument.allow_document_upload
        ),
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
        name='geoCoverage',
        required = False,
        widget=SelectionWidget(
            label='Geographical coverage',
            label_msgid='eea.soer_label_geocoverage',
            i18n_domain='eea.soer',
            format='select',
        ),
        vocabulary=NamedVocabulary('eea.soer.vocab.geo_coverage'),
        enforceVocabulary=True,

    ),


    StringField(
        name='topic',
        required = True,
        widget=SelectionWidget(
            label='Topics',
            label_msgid='eea.soer_label_topics',
            i18n_domain='eea.soer',
            format='select',
        ),
        vocabulary=NamedVocabulary('eea.soer.vocab.topics'),
        enforceVocabulary=True,
    ),

    StringField(
        name='question',
        required = True,
        widget=SelectionWidget(
            label='Question',
            label_msgid='eea.soer_label_questions',
            i18n_domain='eea.soer',
            format='select',
        ),
        vocabulary=NamedVocabulary('eea.soer.vocab.questions'),
        enforceVocabulary=True,
    ),

    StringField(
        name='evaluation',
        required=0,
        searchable=0,
        default='',
        widget=StringWidget(
            lagel='Evaluation',
            label_msgid='label_evaluation',
            description='This is a two letter value which indicates quickly what the evaluation and trend is.',
            visible={'view' : 'invisible'},
        ),
    ),
),
)

schema = getattr(ATFolder, 'schema', Schema(())).copy() + schema.copy()
schema['title'].default = 'not_set_yet'
schema['soerCountry'].default_method = 'default_country'

class SOERReport(ATFolder, ATNewsItem):
    """ """
    security = ClassSecurityInfo()
    __implements__ = (getattr(ATFolder,'__implements__',()),)
    implements(ISOERReport)

    meta_type = 'SOERReport'
    portal_type = 'SOERReport'
    _at_rename_after_creation = True

    schema = schema
    content_icon = 'document_icon.gif'

    original_url = ''
    
    def getTermTitle(self, vocab_name, term_key):
        """Utility method to get the title form a vocabulary term"""
        portal = getToolByName(self, 'portal_url').getPortalObject()
        atvm = getToolByName(portal, ATVOCABULARYTOOL, None)
        vocab = atvm.getVocabularyByName(vocab_name)
        term = getattr(vocab, term_key, None)
        if term == None:
            return ''
        return term.title;

    def getSoerCountryName(self):
        return self.getTermTitle('eea.soer.vocab.european_countries', self.getSoerCountry())

    def default_country(self):
        path = self.getPhysicalPath()
        if len(path) >= 2:
            if self.aq_parent.portal_type == self.portal_type:
                country_code = path[-3]
            else:
                country_code = path[-2]
            return country_code
        return ''

    def figures(self):
        """ return figures for listing at the bottom of the report """
        assessment = self.getText()
        return Batch([fig  for fig in self.getFolderContents(contentFilter={'portal_type' : 'Image'}) 
                      if fig.getURL() not in assessment ],
                     10)

                
    def isFromFeed(self):
        """ return True if SOERCountry has a feed url """
        if hasattr(self.aq_parent, 'getRdfFeed'):
            return self.aq_parent.getRdfFeed() and True or False
        return False
        
