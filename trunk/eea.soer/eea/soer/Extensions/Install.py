from Products.CMFCore.utils import getToolByName


PROFILE = 'eea.soer:default'


def install(self, reinstall=False):
    portal_setup = getToolByName(self, 'portal_setup')
    portal_setup.setImportContext('profile-%s' % PROFILE)
    portal_setup.runAllImportSteps()
    product_name = PROFILE.split(':')[0]
    qi = getToolByName(self, 'portal_quickinstaller')
    qi.notifyInstalled(product_name)
