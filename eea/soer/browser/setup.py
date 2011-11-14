""" Browser setup module
"""
import os
import urllib2
from Acquisition import aq_base
from zope.interface import directlyProvides
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from Globals import package_home
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import log
from eea.soer.config import GLOBALS
from eea.soer.content.interfaces import ISoerFigure, ISoerDataFile
from eea.facetednavigation.browser.app.exportimport import FacetedExportImport
from p4a.subtyper.interfaces import ISubtyper

facetedMain = os.path.join(package_home(GLOBALS),
                    'browser', 'faceted-main.xml')
facetedCountry = open(os.path.join(package_home(GLOBALS),
                    'browser', 'faceted-country.xml'),'r').read()

class Countries(object):
    """ Countries
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        context = self.context
        vocab = getToolByName(context, 'portal_vocabularies')
        european_countries = vocab['eea.soer.vocab.european_countries']
        subtyper = getUtility(ISubtyper)
        subtyper.change_type(context,
                        'eea.facetednavigation.FolderFacetedNavigable')
        faceted = FacetedExportImport(context, context.REQUEST)
        faceted.import_xml(import_file=facetedMain)
        for country_code in european_countries.keys():
            if hasattr(aq_base(context), country_code):
                continue
            mapurl = u'http://map.eea.europa.eu/getmap.asp?Fullextent=1&' \
                    'imagetype=3&size=W600&PredefShade=GreenRed&Q=%s'
            print 'Creating folder with id %s and title %s' % (country_code,
                                        european_countries[country_code].title)
            folder = context[context.invokeFactory('SOERCountry',
                                                    id=country_code)]
            folder.setTitle(european_countries[country_code].title)
            mapurl = mapurl % country_code
            image = urllib2.urlopen(mapurl)
            image_data = image.read()
            if image_data:
                mapimage = folder[folder.invokeFactory('Image', id='%s_map.png'
                                            % country_code, image=image_data)]
                mapimage.unmarkCreationFlag()
                mapimage.setTitle('Map of %s' %
                                european_countries[country_code].title)
                mapimage.setDescription('Map of %s from %s' % (
                                european_countries[country_code].title, mapurl))

            folder.unmarkCreationFlag()
            folder.reindexObject()

            subtyper.change_type(folder,
                        'eea.facetednavigation.FolderFacetedNavigable')

            faceted = FacetedExportImport(folder, folder.REQUEST)
            faceted.import_xml(import_file=facetedCountry.replace(
                '<element value="se"/>','<element value="%s"/>' %
                country_code).replace(' name="se" ',' name="%s" '
                                                    % country_code))

class Migration(object):
    """ Migration class
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.soerImagesAndLinks()
        self.recreateScales()
        self.regenerateTitles()
        self.removeOldCountryMaps()

    def soerImagesAndLinks(self):
        """ Soer Images and Links method
        """
        context = self.context
        cat = getToolByName(context, 'portal_catalog')
        for b in cat(object_provides='eea.soer.content.interfaces.ISOERReport'):
            obj = b.getObject()
            for fig in obj.getFolderContents(
                   contentFilter={'portal_type' : 'Image'}, full_objects=True):
                if not ISoerFigure.providedBy(fig):
                    directlyProvides(fig, ISoerFigure)
                    log.log('MIGRATED figure %s' % fig.absolute_url())

            for link in obj.getFolderContents(
                    contentFilter={'portal_type' : ['Link', 'DataSourceLink']},
                    full_objects=True):
                if not ISoerDataFile.providedBy(link):
                    directlyProvides(link, ISoerDataFile)
                    log.log('MIGRATED data sourc %s' % link.absolute_url())

    def recreateScales(self):
        """ Recreate Scales
        """
        context = self.context
        cat = getToolByName(context, 'portal_catalog')
        for brain in cat(
                object_provides='eea.soer.content.interfaces.ISoerFigure'):
            obj = brain.getObject()
            if obj is None:
                continue
            if hasattr(obj, 'image_preview'):
                continue

            try:
                state = obj._p_changed
            except Exception:
                state = 0

            field = obj.getField('image')
            if field is not None:
                if field.getScale(obj, 'preview'):
                    continue

                log.log('UPDATING scales for  %s' % obj.absolute_url())
                field.removeScales(obj)
                field.createScales(obj)

            if state is None:
                obj._p_deactivate()

    def regenerateTitles(self):
        """ Regenerate Titles
        """
        context = self.context
        cat = getToolByName(context, 'portal_catalog')
        for b in cat(portal_type=['CommonalityReport',
            'FlexibilityReport', 'DiversityReport']):
            obj = b.getObject()
            log.log("UPDATING title '%s'" % obj.Title())
            notify( ObjectModifiedEvent(obj) )

    def removeOldCountryMaps(self):
        """ Removes Old Country Maps
        """
        context = self.context
        cat = getToolByName(context, 'portal_catalog')
        for b in cat(portal_type='SOERCountry'):
            obj = b.getObject()
            mapid = '%s_map.png' % obj.getId()
            if hasattr(obj, mapid):
                log.log('Deleting old map %s for %s' %(
                                                mapid, obj.absolute_url()))
                obj.manage_delObjects(ids=[mapid])

class MigrationFaceted(object):
    """ Migration Faceted
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.reloadFacetedNavigation()

    def reloadFacetedNavigation(self):
        """ Reload faceted configuration for all countries
        """
        subtyper = getUtility(ISubtyper)
        for folder in self.context.getFolderContents(
                contentFilter={ 'portal_type' : 'SOERCountry'},
                                            full_objects=True):
            country_code = folder.getId()
            subtyper.change_type(folder,
                    'eea.facetednavigation.FolderFacetedNavigable')
            log.log('UPDATING facted configuration for %s'
                                % folder.absolute_url())
            faceted = FacetedExportImport(folder, folder.REQUEST)
            faceted.import_xml(import_file=facetedCountry.replace(
                '<element value="se"/>','<element value="%s"/>'
                % country_code).replace(' name="se" ',' name="%s" '
                % country_code))

class SenseFeeds(object):
    """ Setup sense feeds for countries and update them
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        context = self.context
        deleteOld = bool(self.request.get('deleteOld', False))
        updateFeed = bool(self.request.get('updateFeed', False))
        feeds = {'bg' : ['http://nfp-bg.eionet.eu.int/soer-2010/part-c/rdf'],
                 'be' : ['http://nfp.irceline.be/soer-2010/@@rdf'],
                 'sk' :
  ['http://tsense.sazp.sk/Plone/soer-2010-part-c/slovakia/@@rdf'],
                 'ie' :
  ['http://www.epa.ie/environmentinfocus/socio-economic/index.rdf',
   'http://www.epa.ie/environmentinfocus/climatechange/index.rdf',
   'http://www.epa.ie/environmentinfocus/air/index.rdf',
   'http://www.epa.ie/environmentinfocus/water/index.rdf',
   'http://www.epa.ie/environmentinfocus/waste/index.rdf',
   'http://www.epa.ie/environmentinfocus/land/index.rdf',
   'http://www.epa.ie/environmentinfocus/nature/index.rdf',
   'http://www.epa.ie/environmentinfocus/socio-economic/greeneconomy/index.rdf',
   'http://www.epa.ie/environmentinfocus/socio-economic/'
   'irishsustainabledevelopmentmodel/index.rdf'],
                 'no' : ['http://www.miljostatus.no/rdf'],
                 'ro' : ['http://www.anpm.ro/soerstories/rdf'],
                 'si' :
  ['http://www.arso.gov.si/en/soer/air_pollution.rdf',
   'http://www.arso.gov.si/en/soer/alps.rdf',
   'http://www.arso.gov.si/en/soer/bear_story.rdf',
   'http://www.arso.gov.si/en/soer/biodiversity.rdf',
   'http://www.arso.gov.si/en/soer/climate_change.rdf',
   'http://www.arso.gov.si/en/soer/country_introduction.rdf',
   'http://www.arso.gov.si/en/soer/freshwater.rdf',
   'http://www.arso.gov.si/en/soer/land.rdf',
   'http://www.arso.gov.si/en/soer/waste.rdf'], # Alps works, rest are broken
                 'it' :
  ['http://www.sense.sinanet.isprambiente.it/Plone/air-pollution/@@rdf',
   'http://www.sense.sinanet.isprambiente.it/Plone/climate-change/@@rdf',
   'http://www.sense.sinanet.isprambiente.it/Plone/waste/@@rdf',
   'http://www.sense.sinanet.isprambiente.it/Plone/nature-protection-and-biodiversity/@@rdf',
   'http://www.sense.sinanet.isprambiente.it/Plone/land/@@rdf',
   'http://www.sense.sinanet.isprambiente.it/Plone/diversity/@@rdf',
   'http://www.sense.sinanet.isprambiente.it/Plone/freshwater/@@rdf',
   'http://www.sense.sinanet.isprambiente.it/Plone/flexibility-alps/@@rdf',
   'http://www.sense.sinanet.isprambiente.it/Plone/flexibility-local-authorities/@@rdf',
   'http://www.sense.sinanet.isprambiente.it/Plone/flexibility-organic-farming/@@rdf',
   'http://www.sense.sinanet.isprambiente.it/Plone/flexibility-white-certificates/@@rdf'],
                 'cz' : ['http://issar.cenia.cz/issar/add/CZ_SOER.rdf'], # Questions don't follow specification
                 'de' : ['http://sites.uba.de/SOER/frm/Diversity.xml',
                         'http://sites.uba.de/SOER/frm/Air-pollution.xml',
                         'http://sites.uba.de/SOER/frm/Freshwater.xml',
                         'http://sites.uba.de/SOER/frm/Climate-change.xml',
                         'http://sites.uba.de/SOER/frm/Land.xml',
                         'http://sites.uba.de/SOER/frm/Waste.xml',
                         'http://sites.uba.de/SOER/frm/Biodiversity.xml',
                         'http://sites.uba.de/SOER/frm/Flexibility.xml'], # Waiting for feeds
                 'at' : ['http://www.umweltbundesamt.at/rdf_eea'],
                 'se' :
  ['http://www.naturvardsverket.se/en/In-English/Menu/GlobalMenu/Sense---RDF'], # Unaccessible, password protected, they are working on it
                 'rs' :
  ['http://www.report.sepa.gov.rs/soer-2010-serbia/@@rdf'],
                                  }
        for country_code, urls in feeds.items():
            if hasattr(aq_base(context), country_code):
                log.log("SENSE setup of '%s'" % country_code)
                country = context[country_code]
                if country.getRdfFeed() and deleteOld:
                    log.log("SENSE setup of '%s' found old feeds, deleting "
                            "them" % country_code)
                    oldFeedIds = [b.getId for b in country.getFolderContents(
                                      contentFilter={'portal_type' : 'Link'})]
                    country.manage_delObjects(ids=oldFeedIds)
                    country.setRdfFeed('')
                if not country.getRdfFeed():
                    country.setRdfFeed(urls[0])
                    log.log("SENSE setup adding feed %s to '%s'" %
                                                     (urls[0], country_code))
                    for url in urls[1:]:
                        feed = country[ country.invokeFactory(
                                                         'Link', id='tmplink',
                                                         title=url,
                                                         remoteUrl=url)]
                        feed._renameAfterCreation(check_auto_id=False)
                        log.log("SENSE setup adding feed %s to '%s'" %
                                                        (url, country_code))
                else:
                    log.log("SENSE setup found old feeds in '%s' skipping "
                            "setup" % country_code)
                if updateFeed:
                    country.updateFromFeed()
            else:
                log.log("SENSE setup did NOT find '%s' no feeds "
                        "were setup." % country_code)

class FeedUpdater(object):
    """ Update all feeds or the choosen one if they have a feed set
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, country=None):
        """ Call /soer/@@senseFeedUpdate?country=se to just update selected
            country, Sweden. The user who calls this script needs to be able to
            delete/create and publish content in /soer section.
        """
        context = self.context
        query = { 'portal_type' :'SOERCountry' }
        country = self.request.get('country', country)
        if country is None:
            return 'provide countries or update=all to update all countries'
        query['getId'] = country
        cat = getToolByName(context, 'portal_catalog')
        out = []
        #kwargs = {'Importance': 'Normal',
        #          'X-MSMail-Priority': 'Normal',
        #          'X-Priority': '3',
        #          'Priority': 'normal'}
        #subject = 'SENSE Feed update (OK)'
        #error = None
        for b in cat(query):
            obj = b.getObject()
            if obj.getRdfFeed():
                obj.updateFromFeed()
                out.append({'country' : b.Title,
                                'url' : b.getURL(),
                                'feed' : obj.getRdfFeed(),
                                'status' : 'OK' })
        msg = context.unrestrictedTraverse('mail_feed_update')
        msg = msg(status=out)

        return msg
