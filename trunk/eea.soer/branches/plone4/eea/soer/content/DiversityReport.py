""" Diversity Report
"""
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from eea.soer.content.interfaces import IDiversityReport
from eea.soer.content.SOERReport import schema as  SOERReportSchema, SOERReport
from eea.soer.config import PROJECTNAME
from eea.soer import vocab
from Products.ATVocabularyManager import NamedVocabulary
try:
    from Products.LinguaPlone.public import Schema, StringField, StringWidget
    from Products.LinguaPlone.public import registerType
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import Schema, StringField, StringWidget
    from Products.Archetypes.public import registerType

# Make pyflakes happy
__all__ = [Schema, StringField, StringWidget, registerType]

schema = Schema((
        StringField(
        name='topic',
        required = False,
        default=u'country introduction',
        widget=StringWidget(
            label='Topics',
            label_msgid='eea.soer_label_topics',
            i18n_domain='eea.soer',
            visible={'view' : 'invisible',
                     'edit' : 'invisible'},
            description='country introduction'
         ),
     ),
),)

schema = SOERReportSchema.copy() + schema
schema['question'].vocabulary = \
        NamedVocabulary('eea.soer.vocab.diversity_questions')

class DiversityReport(SOERReport):
    """ Diversity Report
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(SOERReport, '__implements__', ()), )
    implements(IDiversityReport)

    meta_type = 'DiversityReport'
    portal_type = 'DiversityReport'

    schema = schema
    default_view = 'diversity_report_view'

    def getLongSoerQuestion(self):
        """ Get Long Soer Question
        """
        q = self.getQuestion()
        return vocab.long_diversity_questions.get(q, q)

    def default_desc(self):
        """ Default desc
        """
        country = self.getTermTitle('eea.soer.vocab.european_countries',
                                    self.getSoerCountry())
        return 'SOER Country profile from %s' % country

registerType(DiversityReport, PROJECTNAME)

def reportUpdated(obj, event):
    """ Report updated
    """
    country = obj.getTermTitle('eea.soer.vocab.european_countries',
                               obj.getSoerCountry())
    question = obj.getTermTitle('eea.soer.vocab.diversity_questions',
                                obj.getQuestion())
    obj.setTitle('Country profile - %s (%s)' % (question, country))
    if not obj.Description() and not obj.isTemporary():
        obj.setDescription(obj.default_desc())
