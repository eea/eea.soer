""" Setup
"""
from plone.i18n.locales.interfaces import ICountryAvailability
from zope.component import queryUtility
from Products.CMFCore.utils import getToolByName
from eea.soer.vocab import atvocabs as vocabs
from eea.vocab import countries
from eea.soer import transform
from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
import logging

logger = logging.getLogger('eea.soer.setuphandlers')

def reindexSoerReports(context):
    """ Reindex Soer Reports
    """
    portal = context.getSite()
    catalog = portal.portal_catalog
    result = catalog.searchResults(
        {'object_provides': 'eea.soer.content.interfaces.ISOERReport',
         'Language': 'all'})
    for i in result:
        i.getObject().reindexObject()

def setupCountriesVocabulary(context):
    """ Setup Countries Vocabulary
    """
    vocabs['eea.soer.vocab.european_countries'] = []
    util = queryUtility(ICountryAvailability)
    all_countries = util.getCountries()
    european_country_codes = countries.getCountries()
    for i in european_country_codes:
        country_name = all_countries[i][u'name']
        vocabs['eea.soer.vocab.european_countries'].append((i, country_name))

def setupTransform(context):
    """ Setup Transform
    """
    portal = context.getSite()
    ptr = getToolByName(portal, 'portal_transforms')
    if 'image_with_source' not in ptr.objectIds():
        ptr.registerTransform(transform.register())

def hideFromNavigation(context):
    """ Hide From Navigation
    """
    portal = context.getSite()
    props = getToolByName(portal, 'portal_properties')
    portalTypes = ['CommonalityReport',
                   'FlexibilityReport',
                   'DiversityReport',
                   'RelatedIndicatorLink']
    hidden =  list(props.navtree_properties.metaTypesNotToList)
    for t in portalTypes:
        if t not in hidden:
            hidden.append(t)
    props.navtree_properties.manage_changeProperties(metaTypesNotToList=hidden)

def setupATVocabularies(context):
    """ Installs all AT-based Vocabularies
    """
    if context.readDataFile('eea.soer.txt') is None:
        return

    # if we have eeasoer_vocabularies.txt vocabularies are replaced
    # used when vocabularies need to be upgraded
    replace = bool(context.readDataFile('eeasoer_vocabularies.txt'))

    portal = context.getSite()
    atvm = getToolByName(portal, ATVOCABULARYTOOL, None)
    if atvm is None:
        return
    setupCountriesVocabulary(context)
    for vkey in vocabs.keys():
        if hasattr(atvm, vkey):
            if not replace:
                continue
            atvm.manage_delObjects(ids=[vkey])

        logger.info("Adding vocabulary %s" % vkey)

        atvm.invokeFactory('SimpleVocabulary', vkey)
        simple = atvm.getVocabularyByName(vkey)
        for (key, val) in vocabs[vkey]:
            simple.addTerm(key, val)

def installProductsMarshall(context):
    """ Install Products.Marshall
    """
    if context.readDataFile('eea.soer.txt') is None:
        return

    logger.info("Installing Products.Marshall")

    site = context.getSite()
    qinstaller = getToolByName(site, 'portal_quickinstaller')
    qinstaller.installProduct('Marshall')

def setupVarious(context):
    """ Setup various
    """
    if context.readDataFile('eea.soer.txt') is None:
        return
    setupTransform(context)
    hideFromNavigation(context)
    installProductsMarshall(context)
