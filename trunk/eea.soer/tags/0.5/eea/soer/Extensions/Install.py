from Products.CMFCore.utils import getToolByName
import transaction


PROFILES = [ 'eea.rdfmarshaller:default', 'eea.soer:default']
PRODUCT_DEPENDENCIES = ['ATVocabularyManager', 'eea.vocab']


def install(self, reinstall=False):
    qi = getToolByName(self, 'portal_quickinstaller')
    for i in PRODUCT_DEPENDENCIES:
        if reinstall and qi.isProductInstalled(i):
            qi.reinstallProducts([i])
            transaction.savepoint()
        elif not qi.isProductInstalled(i):
            qi.installProduct(i)
            transaction.savepoint()
    portal_setup = getToolByName(self, 'portal_setup')
    for profile in PROFILES:
        portal_setup.setImportContext('profile-%s' % profile)
        portal_setup.runAllImportSteps()
        product_name = profile.split(':')[0]
        qi.notifyInstalled(product_name)

    migrationTool = getToolByName(self, 'portal_migration')
    if migrationTool.getInstanceVersionTuple()[0] >= 3:
        portal_setup.runAllImportStepsFromProfile('profile-eea.soer:plone3')
         

