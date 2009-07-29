from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.folder import ATFolder
from eea.soer.interfaces import ISOERReport
from eea.soer.config import *
try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import *


class SOERReport(ATFolder):
    """ """
    implements(ISOERReport)
    security = ClassSecurityInfo()


registerType(SOERReport, PROJECTNAME)
