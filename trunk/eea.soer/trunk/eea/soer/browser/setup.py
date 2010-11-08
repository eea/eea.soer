import os
import urllib2
from Acquisition import aq_base
from zope.interface import directlyProvides
from zope.component import getUtility
from Globals import package_home
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import log

from eea.soer.config import GLOBALS
from eea.soer.content.interfaces import ISoerFigure, ISoerDataFile
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
            mapurl = u'http://map.eea.europa.eu/getmap.asp?Fullextent=1&imagetype=3&size=W600&PredefShade=GreenRed&Q=%s'
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
    

class Migration(object):
    """ """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.soerImagesAndLinks()
        
    def soerImagesAndLinks(self):
        context = self.context
        cat = getToolByName(context, 'portal_catalog')
        for b in cat(object_provides='eea.soer.content.interfaces.ISOERReport'):
            obj = b.getObject()
            for fig in obj.getFolderContents(contentFilter={'portal_type' : 'Image'}, full_objects=True):
                if not ISoerFigure.providedBy(fig):
                    directlyProvides(fig, ISoerFigure)
                    log.log('MIGRATED figure %s' % fig.absolute_url())
                    
            for link in obj.getFolderContents(contentFilter={'portal_type' : ['Link', 'DataSourceLink']}, full_objects=True):
                if not ISoerDataFile.providedBy(link):
                    directlyProvides(link, ISoerDataFile)
                    log.log('MIGRATED data sourc %s' % link.absolute_url())


class SenseFeeds(object):
    """ setup sense feeds for countries and update them """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        context = self.context
        deleteOld = bool(self.request.get('deleteOld', False))
        updateFeed = bool(self.request.get('updateFeed', False))        
        feeds = {'bg' : ['http://nfp-bg.eionet.eu.int/soer-2010/part-c/rdf'], #Bulgaria
                 'be' : ['http://nfp.irceline.be/soer-2010/@@rdf'], #Belgium
                 'sk' : ['http://tsense.sazp.sk/Plone/soer-2010-part-c/slovakia/@@rdf'], #Slovakia
                 'ie' : ['http://www.epa.ie/environmentinfocus/socio-economic/index.rdf',
                         'http://www.epa.ie/environmentinfocus/climatechange/index.rdf',
                         'http://www.epa.ie/environmentinfocus/air/index.rdf',
                         'http://www.epa.ie/environmentinfocus/water/index.rdf',
                         'http://www.epa.ie/environmentinfocus/waste/index.rdf',
                         'http://www.epa.ie/environmentinfocus/land/index.rdf',
                         'http://www.epa.ie/environmentinfocus/nature/index.rdf',
                         'http://www.epa.ie/environmentinfocus/socio-economic/greeneconomy/index.rdf',
                         'http://www.epa.ie/environmentinfocus/socio-economic/irishsustainabledevelopmentmodel/index.rdf'], #Ireland
                 'no' : ['http://www.miljostatus.no/rdf'], #Norway
                 'ro' : ['http://www.anpm.ro/soerstories/rdf'], #Romania
                 'si' : ['http://www.arso.gov.si/en/soer/alps.rdf',
                         #'http://www.arso.gov.si/en/soer/biodiversity.rdf',
                         #'http://www.arso.gov.si/en/soer/bear%20story.rdf',
                         #'http://www.arso.gov.si/en/soer/country%20introduction.rdf',
                         #'http://www.arso.gov.si/en/soer/land.rdf'
                         ], #Slovenia (alps worsk, rest broken)
                 'it' : ['http://www.sense.sinanet.isprambiente.it/Plone/italian-soer-part-c/@@rdf'], #Italy (short feed)
                 'nl' : ['http://www.pbl.nl/sense/'], #Netherlands (short)
                 #'cz' : ['http://issar.cenia.cz/issar/add/CZ_SOER.rdf'], #Chech Republic (questins don't follow specification)
                 'de' : ['http://sites.uba.de/SOER/dat/Diversity.xml',
                         'http://sites.uba.de/SOER/dat/Air-pollution.xml',
                         'http://sites.uba.de/SOER/dat/Freshwater.xml',
                         'http://sites.uba.de/SOER/dat/Climate-change.xml',
                         'http://sites.uba.de/SOER/dat/Land.xml',
                         'http://sites.uba.de/SOER/dat/Waste.xml',
                         'http://sites.uba.de/SOER/dat/Biodiversity.xml',
                         'http://sites.uba.de/SOER/dat/Flexibility.xml'], #Germany 
                 #'at' : ['http://www.umweltbundesamt.at/rdf_eea'], #Austria (broken)
                 #'se' : ['http://www.naturvardsverket.se/en/In-English/Menu/GlobalMenu/Sense---RDF/'], #Sweden (unaccessible, password protected, they are working on it)
                 } 
        for country_code, urls in feeds.items():
            if hasattr(aq_base(context), country_code):
                log.log("SENSE setup of '%s'" % country_code)
                country = context[country_code]
                if country.getRdfFeed() and deleteOld:
                    log.log("SENSE setup of '%s' found old feeds, deleting them" % country_code)
                    oldFeedIds = [b.getId for b in country.getFolderContents(contentFilter={'portal_type' : 'Link'})]
                    country.manage_delObjects(ids=oldFeedIds)
                    country.setRdfFeed('')
                if not country.getRdfFeed():
                    country.setRdfFeed(urls[0])
                    log.log("SENSE setup adding feed %s to '%s'" % (urls[0], country_code))
                    for url in urls[1:]:                    
                        feed = country[ country.invokeFactory('Link', id='tmplink',
                                                              title=url,
                                                              remoteUrl=url) ]
                        newId = feed._renameAfterCreation(check_auto_id=False)
                        log.log("SENSE setup adding feed %s to '%s'" % (url, country_code))
                else:
                    log.log("SENSE setup found old feeds in '%s' skipping setup" % country_code)
                if updateFeed:
                    country.updateFromFeed()
            else:
                log.log("SENSE setup did NOT find '%s' no feeds were setup." % country_code)
                
                        
