import os
import urllib2
from Acquisition import aq_base
from zope.component import getUtility
from Globals import package_home
from Products.CMFCore.utils import getToolByName
from eea.soer.config import GLOBALS
from eea.facetednavigation.browser.app.exportimport import FacetedExportImport
from p4a.subtyper.interfaces import ISubtyper

facetedMain = os.path.join(package_home(GLOBALS), 'Extensions', 'faceted-main.xml')
facetedCountry = open(os.path.join(package_home(GLOBALS), 'Extensions', 'faceted-country.xml'),'r').read()


class Countries(object):
    """ """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def __call__(self):
        context = self.context
        vocab = getToolByName(context, 'portal_vocabularies')
        european_countries = vocab['eea.soer.vocab.european_countries']
        subtyper = getUtility(ISubtyper)
        subtyper.change_type(context, 'eea.facetednavigation.FolderFacetedNavigable')
        faceted = FacetedExportImport(context, context.REQUEST)
        faceted.import_xml(import_file=facetedMain)
        for country_code in european_countries.keys():
            if hasattr(aq_base(context), country_code):
                continue
            mapurl = u'http://map.eea.europa.eu/getmap.asp?Fullextent=1&imagetype=3&size=W600&PredefShade=GreenRed&Q=%s:2'
            print 'Creating folder with id %s and title %s' % (country_code, european_countries[country_code].title)
            folder = context[context.invokeFactory('SOERCountry', id=country_code)]
            folder.setTitle(european_countries[country_code].title)
            mapurl = mapurl % country_code
            image = urllib2.urlopen(mapurl)
            image_data = image.read()
            if image_data:
                mapimage = folder[folder.invokeFactory('Image', id='%s_map.png' % country_code,
                                                  image=image_data)]
                mapimage.unmarkCreationFlag()
                mapimage.setTitle('Map of %s' % european_countries[country_code].title)
                mapimage.setDescription('Map of %s from %s' % (european_countries[country_code].title, mapurl))

            folder.unmarkCreationFlag()
            folder.reindexObject()

            subtyper.change_type(folder, 'eea.facetednavigation.FolderFacetedNavigable')

            faceted = FacetedExportImport(folder, folder.REQUEST)
            faceted.import_xml(import_file=facetedCountry.replace('<element value="se"/>','<element value="%s"/>' % country_code))
    
