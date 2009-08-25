from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.newsitem import ATNewsItem
from eea.soer.content.interfaces import ICommonalityReport
from eea.soer.content.SOERReport import SOERReport
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

),
)

schema = getattr(SOERReport, 'schema', Schema(())).copy() + schema.copy()
schema['description'].default_method = 'default_desc'


class CommonalityReport(SOERReport):
    """ """
    security = ClassSecurityInfo()
    __implements__ = (getattr(SOERReport,'__implements__',()),)
    implements(ICommonalityReport)

    meta_type = 'CommonalityReport'
    portal_type = 'CommonalityReport'

    schema = schema
    default_view = 'commonality_report_view'

    def short_topic(self):
        topic = self.getSoerTopic()
        if '-' in topic:
            return topic.split('-')[0]
        return topic.strip()

    def long_section(self):
        section = self.getSoerSection()
        return vocab.long_sections.get(section, 'Section not found')

    def default_desc(self):
        lang_code = self.getPhysicalPath()[-2]
        desc = 'SOER Part C Commonality Report from %s' % vocab.european_countries.get(lang_code, 'Unknown Country')
        return desc


registerType(CommonalityReport, PROJECTNAME)

def gen_title(obj, evt):
    new_title = obj.short_topic() + ' - ' + obj.getSoerSection()
    obj.setTitle(new_title)
