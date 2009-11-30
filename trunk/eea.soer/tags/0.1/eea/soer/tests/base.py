from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.GenericSetup import EXTENSION, profile_registry


PRODUCTS = ['ATVocabularyManager', 'FiveSite']
PROFILES = ['eea.soer:default']


@onsetup
def setup_soer():
    fiveconfigure.debug_mode = True
    import Products.Five
    import Products.FiveSite
    import eea.soer
    zcml.load_config('meta.zcml', Products.Five)
    zcml.load_config('configure.zcml', Products.Five)
    zcml.load_config('configure.zcml', Products.FiveSite)
    zcml.load_config('configure.zcml', eea.soer)
    fiveconfigure.debug_mode = False

    PloneTestCase.installProduct('Five')
    for product in PRODUCTS:
        PloneTestCase.installProduct(product)

setup_soer()
PRODUCTS.append('eea.soer')
PloneTestCase.setupPloneSite(products=PRODUCTS)


class SOERFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    
    def afterSetUp(self):
        self.setRoles(['Manager'])

        # Let's set up the folder structure. This is important since title and
        # description is generated from it.

        self.portal.invokeFactory('Folder', id='SOER')
        self.portal.SOER.invokeFactory('Folder', id='se')
