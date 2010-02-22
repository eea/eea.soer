from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.newsitem import ATNewsItem
from eea.soer.content.interfaces import ICommonalityReport
from eea.soer.content.SOERReport import SOERReport
from eea.soer.config import *
from eea.soer import vocab
from Products.ATVocabularyManager import NamedVocabulary
from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import *

schema = getattr(SOERReport, 'schema', Schema(())).copy() 
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

    def default_desc(self):
        country = self.getTermTitle('eea.soer.vocab.european_countries', self.getSoerCountry())
        desc = 'SOER Part C Commonality Report from %s' % country
        return desc

    def getLongSoerQuestion(self):
        return vocab.long_questions[self.getSoerQuestion()]

    def getLongSoerTopic(self):
        return vocab.long_topics[self.getSoerTopic()]


registerType(CommonalityReport, PROJECTNAME)

def gen_title(obj, evt):
    topic = obj.getTermTitle('eea.soer.vocab.topics', obj.getSoerTopic())
    section = obj.getTermTitle('eea.soer.vocab.questions', obj.getSoerQuestion())
    country = obj.getTermTitle('eea.soer.vocab.european_countries', obj.getSoerCountry())
    t = '%s - %s (%s)' % (topic, section, country)
    obj.setTitle(t)
