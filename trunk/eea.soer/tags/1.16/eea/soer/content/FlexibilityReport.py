from zope.interface import implements
from AccessControl import ClassSecurityInfo
#from Products.ATContentTypes.configuration import zconf
#from Products.ATContentTypes.content.folder import ATFolder
#from Products.ATContentTypes.content.newsitem import ATNewsItem
from eea.soer.content.interfaces import IFlexibilityReport
from eea.soer.content.SOERReport import SOERReport
from eea.soer.config import PROJECTNAME
#from eea.soer import vocab
#from Products.ATVocabularyManager import NamedVocabulary
try:
    from Products.LinguaPlone.public import Schema, StringField, StringWidget
    from Products.LinguaPlone.public import registerType
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import Schema, StringField, StringWidget #pyflakes
    from Products.Archetypes.public import registerType

schema = Schema((
        StringField(
        name='topic',
        required = True,
        widget=StringWidget(
            label='Topics',
            label_msgid='eea.soer_label_topics',
            i18n_domain='eea.soer',
            description='use any environmental term, you can find all terms at'\
            ' <a href="http://glossary.eea.europa.eu/">ETDS</a>'
         ),
     ),

    StringField(
        name='question',
        required = True,
        widget=StringWidget(
            label='Title',
            label_msgid='eea.soer_label_questions',
            i18n_domain='eea.soer',
            description='Custom title for this report',
         ),
     ),
),
)
schema = getattr(SOERReport, 'schema').copy() + schema.copy()
schema['title'].required = False


class FlexibilityReport(SOERReport):
    """ Flexibility Report"""
    security = ClassSecurityInfo()
    __implements__ = (getattr(SOERReport, '__implements__', ()), )
    implements(IFlexibilityReport)

    meta_type = 'FlexibilityReport'
    portal_type = 'FlexibilityReport'

    schema = schema
    default_view = 'flexibility_report_view'

    def default_desc(self):
        country = self.getTermTitle('eea.soer.vocab.european_countries',
                                self.getSoerCountry()).encode('utf8')
        return 'SOER National and regional story from %s' % country


registerType(FlexibilityReport, PROJECTNAME)

def reportUpdated(obj, event):
    country = obj.getTermTitle('eea.soer.vocab.european_countries',
                                obj.getSoerCountry()).encode('utf8')
    t = 'National and regional story (%s) - %s' % (country, obj.getQuestion())
    obj.setTitle(t)
    if not obj.Description() and not obj.isTemporary():
        obj.setDescription(obj.default_desc())

        