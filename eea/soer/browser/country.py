from zope.interface import implements
from eea.soer.interfaces import ICountryView
from Products.CMFCore.utils import getToolByName

class CountryView(object):

    implements(ICountryView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def countryIntroduction(self):
        context = self.context
        catalog = getToolByName(context, 'portal_catalog')
        res = catalog( { 'path' :'/'.join( context.getPhysicalPath()),
                         'portal_type' : 'DiversityReport',
                         'getSoerTopic' : 'country introduction' } )
        if res:
            return res[0].getObject()
        
