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
            if res:
                return res[0].getObject()
        
    def channel(self):
        return getattr(aq_base(self.context), 'channel', None)
        
    def getMapUrl(self):
        country_code = self.context.getId()
        mapImage = getattr(aq_base(self.context), '%s_map.png' % country_code, None)
        if mapImage is not None:
            return mapImage.absolute_url()
        return u'http://map.eea.europa.eu/getmap.asp?Fullextent=1&imagetype=3&size=W600&PredefShade=GreenRed&Q=%s:2'% country_code