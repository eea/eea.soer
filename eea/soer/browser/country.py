""" Country
"""
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from eea.soer.interfaces import ICountryView
from zope.interface import implements
from lxml.html.clean import Cleaner

def get_intro_text(text):
    """ Returns only the first <p> tag and preceding nodes
    """

    #cut the text to the first paragraph
    index = text.lower().find('</p>', 1000)
    if index != -1:
        text = text[:index] +'</p>'

    cleaner = Cleaner(
            scripts=False,
            javascript=False,
            comments=False,
            style=False,
            links=False,
            meta=False,
            page_structure=False,
            processing_instructions=False,
            embedded=False,
            forms=False,
            remove_unknown_tags=True,
            )
    text = cleaner.clean_html(text)

    return text

class CountryView(object):
    """ CountryView
    """
    implements(ICountryView)

    def __init__(self, context, request):
        if context.portal_type in ['SOERCountry', 'DiversityReport',
                                   'CommonalityReport', 'FlexibilityReport']:
            while context.portal_type != 'SOERCountry':
                context = context.aq_parent

        self.context = context
        self.request = request

    def countryIntroduction(self):
        """ Country Introduction
        """
        context = self.context
        if context.portal_type == 'SOERCountry':
            catalog = getToolByName(context, 'portal_catalog')
            res = catalog( { 'path' :'/'.join( context.getPhysicalPath()),
                             'portal_type' : 'DiversityReport',
                             'getSoerTopic' : 'country introduction' } )
            for report in  res:
                obj = report.getObject()
                if obj.getQuestion() == u'10':
                    text = get_intro_text(obj.getText())
                    #text = obj.getText()
                    #index = text.lower().find('</p>', 1000)
                    #if index != -1:
                        #text = text[:index] +'</p>'
                    return { 'title' : obj.Title(),
                             'text' : text }
        return None

    def channel(self):
        """ Channel
        """
        context = aq_base(self.context)
        channel = getattr(context, 'channel', None)
        if channel is not None:
            channel['localLogo'] = False
        if channel is not None and hasattr(context, 'logo'):
            channel['localLogo'] = True
        return channel

    def getMapUrl(self):
        """ Get Map URL
        """
        country_code = self.context.getId()
        mapImage = getattr(aq_base(self.context),
                '%s_map.png' % country_code, None)
        if mapImage is not None:
            return mapImage.absolute_url()
        return u'http://discomap.eea.europa.eu/map/getmap/getMap.aspx?'\
                'layers=0&c=0:ICC:%s:100,20,40&size=300,300&m=http://'\
                'cow1/ArcGIS/services/Internal/EuroBoundaries_Dyna_WM/'\
                'MapServer' % country_code.upper()


    def getRegionsUrl(self, widget):
        """ Get Regions URL
        """
        context = self.context
        catalog = getToolByName(context, 'portal_catalog')
        regions = []
        result = ''
        for b in catalog( { 'path' :'/'.join( context.getPhysicalPath()),
                            'portal_type' : [
                                'DiversityReport',
                                'CommonalityReport',
                                'FlexibilityReport']} ):
            obj = b.getObject()
            region = obj.getGeoCoverage()
            if region not in regions:
                regions.append(region)
                result += '&%s=%s' % (widget, region)

        return result[1:]
