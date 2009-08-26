from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.newsitem import ATNewsItem
from eea.soer.content.interfaces import IDiversityReport
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
        name='soerSection',
        required = True,
        widget=SelectionWidget(
            label='Sections',
            label_msgid='eea.soer_label_sections',
            i18n_domain='eea.soer',
            format='select',
        ),
        vocabulary=vocab.diversity_questions,
        enforceVocabulary=True,
    ),

),
)

schema = getattr(SOERReport, 'schema').copy() + schema
schema['description'].default_method = 'default_desc'


class DiversityReport(SOERReport):
    """ """
    security = ClassSecurityInfo()
    __implements__ = (getattr(SOERReport,'__implements__',()),)
    implements(IDiversityReport)

    meta_type = 'DiversityReport'
    portal_type = 'DiversityReport'

    schema = schema
    default_view = 'diversity_report_view'

    def default_desc(self):
        lang_code = self.getPhysicalPath()[-2]
        desc = 'SOER Part C Diversity Report from %s' % vocab.european_countries.get(lang_code, 'Unknown Country')
        return desc

    @property
    def short_section(self):
        section = self.getSoerSection()
        if '-' in section:
            return section.split('-')[0]
        return section.strip()


registerType(DiversityReport, PROJECTNAME)

def gen_title(obj, evt):
    new_title = 'Diversity Report: %s (%s)' % (obj.short_section, obj.getSoerCountry())
    obj.setTitle(new_title)
