import os
from Globals import package_home
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.GenericSetup import EXTENSION, profile_registry


PRODUCTS = ['ATVocabularyManager', 'FiveSite', 'eea.rdfmarshaller']
PROFILES = ['eea.soer:default', 'eea.rdfmarshaller:default']

soerrdf = 'file://%s' % os.path.join(package_home(globals()), 'soerfeed.rdf')
examplerdf = 'file://%s' % os.path.join(package_home(globals()), 'multiexample.rdf')
evalrdf = 'file://%s' % os.path.join(package_home(globals()), 'evaluations.rdf')
nutsrdf = 'file://%s' % os.path.join(package_home(globals()), 'nuts.rdf')
# http://rod.eionet.europa.eu/spatial
spatialrdf = 'file://%s' % os.path.join(package_home(globals()), 'spatial.rdf')

@onsetup
def setup_soer():
    fiveconfigure.debug_mode = True
    import Products.Five
    import Products.FiveSite
    import eea.soer
    import eea.rdfmarshaller
    zcml.load_config('meta.zcml', Products.Five)
    zcml.load_config('configure.zcml', Products.Five)
    zcml.load_config('configure.zcml', Products.FiveSite)
    zcml.load_config('configure.zcml', eea.rdfmarshaller)
    zcml.load_config('configure.zcml', eea.soer)

    fiveconfigure.debug_mode = False

    PloneTestCase.installProduct('Five')
    for product in PRODUCTS:
        PloneTestCase.installProduct(product)

setup_soer()
PRODUCTS.append('eea.soer')
PloneTestCase.setupPloneSite(products=PRODUCTS, extension_profiles=PROFILES)


class SOERFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    
    def afterSetUp(self):
        self.setRoles(['Manager'])

        # Let's set up the folder structure. This is important since title and
        # description is generated from it.

        self.portal.invokeFactory('Folder', id='SOER')

    def enableDebugLog(self):
        """ Enable context.plone_log() output from Python scripts """
        import sys ,logging
        from Products.CMFPlone.log import logger
        logger.root.setLevel(logging.INFO)
        logger.root.addHandler(logging.StreamHandler(sys.stdout))

