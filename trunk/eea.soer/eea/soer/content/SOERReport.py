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

    StringField(
        name='soerTopic',
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
        name='soerSection',
        required = True,
        widget=SelectionWidget(
            label='Sections',
            label_msgid='eea.soer_label_sections',
            i18n_domain='eea.soer',
            format='select',
        ),
        vocabulary=vocab.sections,
        enforceVocabulary=True,
    ),

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
            i18n_domain='eea.soer',
            format='select',
        ),
        vocabulary=vocab.content_types,
        enforceVocabulary=True,
        index='FieldIndex:schema',
    ),

    StringField(
        name='soerCountry',
        required = True,
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
            label='RSS Feed',
            label_msgid='eea.soer_label_feed',
            i18n_domain='eea.soer',
        ),
    ),

),
)

schema = getattr(ATFolder, 'schema', Schema(())).copy() + schema.copy()
schema['title'].readOnly = True
schema['title'].widget.visible = 0
schema['description'].default_method = 'default_desc'
schema['soerCountry'].default_method = 'default_country'


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
    default_view = 'soerreport_view'

    def short_topic(self):
        topic = self.getSoerTopic()
        if '-' in topic:
            return topic.split('-')[0]
        return topic

    def long_section(self):
        section = self.getSoerSection()
        return vocab.long_sections.get(section, 'Section not found')

    def default_desc(self):
        lang_code = self.getPhysicalPath()[-2]
        desc = 'SOER Part C Report from %s' % vocab.european_countries.get(lang_code, 'Unknown Country')
        return desc

    def default_country(self):
        lang_code = self.getPhysicalPath()[-2]
        return vocab.european_countries.get(lang_code, '')


registerType(SOERReport, PROJECTNAME)

def gen_title(obj, evt):
    new_title = obj.short_topic() + ' - ' + obj.getSoerSection()
    obj.setTitle(new_title)
