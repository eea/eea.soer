""" Commonality Report
"""
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from eea.soer.content.interfaces import ICommonalityReport
from eea.soer.content.SOERReport import SOERReport
from eea.soer.config import PROJECTNAME
from eea.soer import vocab
from Products.Archetypes.public import Schema, registerType

schema = getattr(SOERReport, 'schema', Schema(())).copy()

class CommonalityReport(SOERReport):
    """ CommonalityReport class
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(SOERReport, '__implements__', ()), )
    implements(ICommonalityReport)

    meta_type = 'CommonalityReport'
    portal_type = 'CommonalityReport'

    schema = schema
    default_view = 'commonality_report_view'

    def getLongSoerQuestion(self):
        """ Get long SOER question
        """
        return vocab.long_questions.get(self.getQuestion(), u'Unknown value')

    def getLongSoerTopic(self):
        """ Get long SOER topic
        """
        return vocab.long_topics.get(self.getTopic(), u'Unknown value')

    def default_desc(self):
        """ Default desc
        """
        country = self.getTermTitle('eea.soer.vocab.european_countries',
                self.getSoerCountry()).encode('utf8')
        return 'SOER Common environmental theme from %s' % country

registerType(CommonalityReport, PROJECTNAME)

def reportUpdated(obj, event):
    """ Report updated
    """
    topic = obj.getTermTitle('eea.soer.vocab.topics', obj.getTopic())
    section = obj.getTermTitle('eea.soer.vocab.questions', obj.getQuestion())
    country = obj.getTermTitle('eea.soer.vocab.european_countries',
                                obj.getSoerCountry())
    t = '%s - %s (%s)' % (topic, section, country)
    obj.setTitle(t)
    if not obj.Description() and not obj.isTemporary():
        obj.setDescription(obj.default_desc())
