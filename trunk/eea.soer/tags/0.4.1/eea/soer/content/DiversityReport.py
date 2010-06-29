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

schema = getattr(SOERReport, 'schema').copy() 
schema['description'].default_method = 'default_desc'
schema['topic'].widget.visible = { 'edit' : 0 }
schema['topic'].default=u'country introduction'
schema['question'].vocabulary=NamedVocabulary('eea.soer.vocab.diversity_questions')

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
        return vocab.long_diversity_questions[self.getQuestion()]

    def default_desc(self):
        country = self.getTermTitle('eea.soer.vocab.european_countries', self.getSoerCountry())
        desc = 'SOER Part C Diversity Report from %s' % country
        return desc


registerType(DiversityReport, PROJECTNAME)

def gen_title(obj, evt):
    country = obj.getTermTitle('eea.soer.vocab.european_countries', obj.getSoerCountry())
    if obj.getTopic() == 'country introduction':
        obj.setTitle('Country introduction (%s)' % country)
    else:
        question = obj.getTermTitle('eea.soer.vocab.diversity_questions', obj.getQuestion())
        t = 'Diversity Report: %s (%s)' % (question, country)
        obj.setTitle(t)
