from plone.i18n.locales.interfaces import ICountryAvailability

from zope.component import queryUtility
from Products.CMFCore.utils import getToolByName
from eea.soer.vocab import atvocabs as vocabs
from eea.vocab import countries

def reindexSoerReports(context):
    portal = context.getSite()
    catalog = portal.portal_catalog
    result = catalog.searchResults({'object_provides': 'eea.soer.content.interfaces.ISOERReport', 'Language': 'all'})
    for i in result:
        i.getObject().reindexObject()

def setupCountriesVocabulary(context):
    vocabs['eea.soer.vocab.european_countries'] = []
    util = queryUtility(ICountryAvailability)
    all_countries = util.getCountries()
    european_country_codes = countries.getCountries()
    for i in european_country_codes:
        country_name = all_countries[i][u'name']
        vocabs['eea.soer.vocab.european_countries'].append((i, country_name))

def setupATVocabularies(context):
    """ Installs all AT-based Vocabularies """

    from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
    portal = context.getSite()
    atvm = getToolByName(portal, ATVOCABULARYTOOL, None)
    if atvm is None:
        return
    setupCountriesVocabulary(context)
    for vkey in vocabs.keys():
        if hasattr(atvm, vkey):
            continue
        
        print "adding vocabulary %s" % vkey
        
        atvm.invokeFactory('SimpleVocabulary', vkey)
        simple = atvm.getVocabularyByName(vkey)
        for (key, val) in vocabs[vkey]:
            simple.addTerm(key, val)



