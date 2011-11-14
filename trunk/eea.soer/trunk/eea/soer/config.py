""" Config
"""
import os
from Globals import package_home
from Products.CMFCore.permissions import AddPortalContent
import surf

surf.ns.register(SOER="http://www.eea.europa.eu/soer/1.0#")
surf.ns.register(
    SOEREVALUATION="http://www.eea.europa.eu/soer/rdfs/evaluation/1.0#")
surf.ns.register(ROD="http://rod.eionet.europa.eu/schema.rdf#")

DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
ADD_CONTENT_PERMISSION = AddPortalContent
GLOBALS = globals()
PROJECTNAME = "eea.soer"

soerrdf = 'file://%s' % os.path.join(package_home(globals()),
                                     'tests/soerfeed.rdf')
examplerdf = 'file://%s' % os.path.join(package_home(globals()),
                                        'tests/multiexample.rdf')
updatedrdf = 'file://%s' % os.path.join(package_home(globals()),
                                        'tests/multiexampleupdated.rdf')
evalrdf = 'file://%s' % os.path.join(package_home(globals()),
                                     'tests/evaluations.rdf')
nutsrdf = 'file://%s' % os.path.join(package_home(globals()),
                                     'tests/nuts.rdf')
# http://rod.eionet.europa.eu/spatial
spatialrdf = 'file://%s' % os.path.join(package_home(globals()),
                                        'tests/spatial.rdf')
