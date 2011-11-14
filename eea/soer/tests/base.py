""" Base
"""
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup
from Products.Five import zcml
from Products.Five import fiveconfigure
import eea.soer
import sys , logging
from Products.CMFPlone.log import logger

PloneTestCase.installProduct('ATVocabularyManager')
PloneTestCase.installProduct('LinguaPlone')


@onsetup
def setup_soer():
    """ Setup
    """
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', eea.soer)
    fiveconfigure.debug_mode = False

    PloneTestCase.installPackage('eea.soer')
    PloneTestCase.installPackage('eea.vocab')
    PloneTestCase.installPackage('eea.rdfmarshaller')
    PloneTestCase.installPackage('eea.facetednavigation')
    PloneTestCase.installPackage('eea.faceted.inheritance')
    PloneTestCase.installPackage('eea.themecentre')
    PloneTestCase.installPackage('p4a.subtyper')

setup_soer()

PloneTestCase.setupPloneSite(extension_profiles=('eea.soer:default',), products=['kupu'])


class SOERFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    """ SOER Functional Test Case
    """

    def afterSetUp(self):
        """ After setup
        """
        self.setRoles(['Manager'])

        # Let's set up the folder structure. This is important since title and
        # description is generated from it.
        self.portal.invokeFactory('Folder', id='SOER')

    def enableDebugLog(self):
        """ Enable context.plone_log() output from Python scripts
        """
        logger.root.setLevel(logging.INFO)
        logger.root.addHandler(logging.StreamHandler(sys.stdout))
