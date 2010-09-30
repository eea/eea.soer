from Products.CMFCore.permissions import AddPortalContent
import surf

surf.ns.register(SOER="http://www.eea.europa.eu/soer/1.0#")
surf.ns.register(SOEREVALUATION="http://www.eea.europa.eu/soer/rdfs/evaluation/1.0#")

DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
ADD_CONTENT_PERMISSION = AddPortalContent
GLOBALS = globals()
PROJECTNAME = "eea.soer"
