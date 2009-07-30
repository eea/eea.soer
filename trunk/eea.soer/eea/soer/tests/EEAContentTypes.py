"""
This module contains parts from Products.EEAContentTypes that we need for our
test environment.

The code below was copied from Products.EEAContentTypes.setup. This is because
Five loads all products available, which includes eea.themecentre. This causes
the 'Allowed Themes' vocabulary from eea.themecentre to be loaded, but the
ATVocabulary it gets its values from is not. Therefore we do it manually. This
avoids a dependency on the heavy EEAContentTypes product.
"""
from Products.CMFCore.utils import getToolByName


vocabs = {}

vocabs['countries'] = (
    ('default', 'Select your country'),
    ('AND','ANDORRA'),
    ('AUT','AUSTRIA'),
    ('BLR','BELARUS'),
    ('BEL','BELGIUM'),
    ('BIH','BOSNIA AND HERZEGOWINA'),
    ('BGR','BULGARIA'),
    ('HRV','CROATIA (local name: Hrvatska)'),
    ('CYP','CYPRUS'),
    ('CZE','CZECH REPUBLIC'),
    ('DNK','DENMARK'),
    ('SLV','EL SALVADOR'),
    ('EST','ESTONIA'),
    ('FJI','FIJI'),
    ('FIN','FINLAND'),
    ('FRA','FRANCE'),
    ('GEO','GEORGIA'),
    ('DEU','GERMANY'),
    ('GRC','GREECE'),
    ('GRL','GREENLAND'),
    ('HUN','HUNGARY'),
    ('ISL','ICELAND'),
    ('IRL','IRELAND'),
    ('ITA','ITALY'),
    ('LVA','LATVIA'),
    ('LTU','LITHUANIA'),
    ('LUX','LUXEMBOURG'),
    ('MKD','THE FORMER YUGOSLAV REPUBLIC OF MACEDONIA,'),
    ('MLT','MALTA'),
    ('MEX','MEXICO'),
    ('MCO','MONACO'),
    ('NLD','NETHERLANDS'),
    ('NOR','NORWAY'),
    ('POL','POLAND'),
    ('PRT','PORTUGAL'),
    ('ROM','ROMANIA'),
    ('RUS','RUSSIAN FEDERATION'),
    ('SVK','SLOVAKIA (Slovak Republic)'),
    ('SVN','SLOVENIA'),
    ('ESP','SPAIN'),
    ('SWE','SWEDEN'),
    ('CHE','SWITZERLAND'),
    ('TUR','TURKEY'),
    ('GBR','UNITED KINGDOM'),
    ('ZZZ','Other'),
)

def setupATVocabularies(portal):
    """ Installs all AT-based Vocabularies """
    
    from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
    
    vkeys = vocabs.keys()
    atvm = getToolByName(portal, ATVOCABULARYTOOL, None)
    if atvm is None:
        return
    
    for vkey in vkeys:

        print "adding vocabulary %s" % vkey
        
        if hasattr(atvm, vkey):
            continue
        
        atvm.invokeFactory('SimpleVocabulary', vkey)
        vocab = atvm[vkey]
        for (ikey, value) in vocabs[vkey]:
            vocab.invokeFactory('SimpleVocabularyTerm', ikey)
            vocab[ikey].setTitle(value)
