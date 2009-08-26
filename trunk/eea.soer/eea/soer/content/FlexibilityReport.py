from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.newsitem import ATNewsItem
from eea.soer.content.interfaces import IFlexibilityReport
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


class FlexibilityReport(SOERReport):
    """ """
    security = ClassSecurityInfo()
    __implements__ = (getattr(SOERReport,'__implements__',()),)
    implements(IFlexibilityReport)

    meta_type = 'FlexibilityReport'
    portal_type = 'FlexibilityReport'

    schema = schema
    default_view = 'flexibility_report_view'

    def default_desc(self):
        lang_code = self.getPhysicalPath()[-2]
        desc = 'SOER Part C Flexibility Report from %s' % vocab.european_countries.get(lang_code, 'Unknown Country')
        return desc


registerType(FlexibilityReport, PROJECTNAME)

def gen_title(obj, evt):
    new_title = 'Flexibility Report (%s)' % obj.getSoerCountry()
    obj.setTitle(new_title)
