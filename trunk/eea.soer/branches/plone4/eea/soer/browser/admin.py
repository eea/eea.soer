""" Admin module for browser package
"""
from zope.interface import implements, Interface
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class IAdminView(Interface):
    """ IAdminView interface
    """

    def info(self):
        """ Return countries and it's reports
        """

class AdminView(BrowserView):
    """ AdminView BrowserView
    """
    implements(IAdminView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def info(self):
        """ Info
        """
        #ret = []
        catalog = getToolByName(self.context, 'portal_catalog')
        countries = catalog(portal_type='SOERCountry')
        result = {'unknown' : { 'title': 'Unknown',
                                'url' : '',
                                'id' : '',
                                'common' : {'reports':[],
                                            'stats': {}},
                                'profile' : {'reports' : [],
                                             'stats' : 0}}
                 }
        for country in countries:
            result[country.getId] = { 'title': country.Title,
                                      'url' : country.getURL(),
                                      'id' : country.getId,
                                      'common' : {'reports':[],
                                                  'stats': {}},
                                      'profile' : {'reports' : [],
                                                   'stats' : 0 }}
            countryIds = result.keys()
        reports = catalog(portal_type=['DiversityReport', 'CommonalityReport'],
                          sort_on='sortable_title',
                          isSubReport=False)
        for brain in reports:
            obj = brain.getObject()
            country = 'unknown'
            if obj.getSoerCountry() in countryIds:
                country = obj.getSoerCountry()
            #handle special cases where gb & montenegro got renamed folder ids
            elif obj.getSoerCountry() == 'gb':
                country = 'uk'
            elif obj.getSoerCountry() == 'montenegro':
                country = 'me'
            country = result[country]
            if obj.portal_type == 'CommonalityReport':
                country['common']['reports'].append(brain)
                noQuestions =  country['common']['stats'].get(
                                                    obj.getTopic(), 0) + 1
                country['common']['stats'][obj.getTopic()] = noQuestions
            else:
                country['profile']['reports'].append(brain)
                country['profile']['stats'] += 1

        return [ c for _unused, c in result.items()]

    __call__ = ViewPageTemplateFile('admin.pt')
