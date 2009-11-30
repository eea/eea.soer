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
        name='soerQuestion',
        required = True,
        widget=SelectionWidget(
            label='Questions',
            label_msgid='eea.soer_label_questions',
            i18n_domain='eea.soer',
            format='select',
        ),
        vocabulary=NamedVocabulary('eea.soer.vocab.diversity_questions'),
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

    def getLongSoerQuestion(self):
        return vocab.long_diversity_questions[self.getSoerQuestion()]

    def default_desc(self):
        country = self.getTermTitle('eea.soer.vocab.european_countries', self.getSoerCountry())
        desc = 'SOER Part C Diversity Report from %s' % country
        return desc


registerType(DiversityReport, PROJECTNAME)

def gen_title(obj, evt):
    question = obj.getTermTitle('eea.soer.vocab.diversity_questions', obj.getSoerQuestion())
    country = obj.getTermTitle('eea.soer.vocab.european_countries', obj.getSoerCountry())
    t = 'Diversity Report: %s (%s)' % (question, country)
    obj.setTitle(t)
