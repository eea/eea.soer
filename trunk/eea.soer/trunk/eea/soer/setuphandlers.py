from Products.CMFCore.utils import getToolByName

def reindexSoerReports(context):
    portal = context.getSite()
    catalog = portal.portal_catalog
    result = catalog.searchResults({'object_provides': 'eea.soer.content.interfaces.ISOERReport', 'Language': 'all'})
    for i in result:
        i.getObject().reindexObject()

def setupATVocabularies(context):
    """ Installs all AT-based Vocabularies """

    from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
    portal = context.getSite()
    atvm = getToolByName(portal, ATVOCABULARYTOOL, None)
    if atvm is None:
        return

    from eea.soer.vocab import atvocabs as vocabs
    for vkey in vocabs.keys():

        if hasattr(atvm, vkey):
            continue
        
        print "adding vocabulary %s" % vkey
        
        atvm.invokeFactory('SimpleVocabulary', vkey)
        simple = atvm.getVocabularyByName(vkey)
        for (key, val) in vocabs[vkey]:
            simple.addTerm(key, val)
