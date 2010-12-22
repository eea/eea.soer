from zope.interface import implements, Interface
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from eea.soer import vocab

class IAdminView(Interface):
    """ """

    def info():
        """ return countries and it's reports """
        
class AdminView(BrowserView):
    implements(IAdminView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def info(self):
        """ """
        ret = []
        catalog = getToolByName(self.context, 'portal_catalog')
        countries = catalog(portal_type='SOERCountry')
        result = {'unknown' : { 'title': 'Unknown',
                                'url' : '',
                                'id' : '',
                                'reports' : []}}
        for country in countries:
            result[country.getId] = { 'title': country.Title,
                                      'url' : country.getURL(),
                                      'id' : country.getId,
                                      'reports' : []}
        countryIds = result.keys()
        reports = catalog(portal_type=['CommonalityReport'],
                          sort_on='sortable_title',
                          isSubReport=False)
        for brain in reports:
            obj = brain.getObject()
            if obj.getSoerCountry() in countryIds:
                result[obj.getSoerCountry()]['reports'].append(brain)
            else:
                result['unknown']['reports'].append(brain)
        return [ c for cid,c in result.items()]

    __call__ = ViewPageTemplateFile('admin.pt')
