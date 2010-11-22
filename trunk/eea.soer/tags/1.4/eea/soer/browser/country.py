from zope.interface import implements
from eea.soer.interfaces import ICountryView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_base

class CountryView(object):

    implements(ICountryView)

    def __init__(self, context, request):
        if context.portal_type in ['SOERCountry', 'DiversityReport', 'CommonalityReport', 'FlexibilityReport']:
            while context.portal_type != 'SOERCountry':
                context = context.aq_parent

        self.context = context
        self.request = request
        

    def countryIntroduction(self):
        context = self.context
        if context.portal_type == 'SOERCountry':
            catalog = getToolByName(context, 'portal_catalog')
            res = catalog( { 'path' :'/'.join( context.getPhysicalPath()),
                             'portal_type' : 'DiversityReport',
                             'getSoerTopic' : 'country introduction' } )
            for report in  res:
                obj = res[0].getObject()
                if obj.getQuestion() == u'10':
                    text = obj.getText()
                    index = text.lower().find('</p>', 1000)
                    if index != -1:
                        text = text[:index] +'</p>'
                    return { 'title' : obj.Title(),
                             'text' : text }
        return None
    
    def channel(self):
        return getattr(aq_base(self.context), 'channel', None)
        
    def getMapUrl(self):
        country_code = self.context.getId()
        mapImage = getattr(aq_base(self.context), '%s_map.png' % country_code, None)
        if mapImage is not None:
            return mapImage.absolute_url()
        return u'http://discomap.eea.europa.eu/map/getmap/getMap.aspx?layers=0&c=0:ICC:%s:100,20,40&size=300,300&m=http://cow1/ArcGIS/services/Internal/EuroBoundaries_Dyna_WM/MapServer' % country_code.upper()
