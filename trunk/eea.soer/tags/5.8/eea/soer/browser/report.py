""" Report module
"""
from zope.interface import implements
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from eea.soer.interfaces import IReportView, IReportQuestionsByTopic
from eea.soer import vocab
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

PARTC_TOPIC_MAP = {
    'climate change': { 'topic' : 'climate change',
                        'image' : '/themes/climate/theme_image/image_icon',
                        'title' : 'Climate change' },
    'biodiversity': { 'topic' : 'nature and biodiversity',
                        'image' : '/themes/biodiversity/theme_image/image_icon',
                        'title' : 'Nature and biodiversity' },
    'land': { 'topic' : 'land use',
                        'image' : '/themes/landuse/theme_image/image_icon',
                        'title' : 'Land' },
    'waste': { 'topic' : 'material resources, natural resources, waste',
                        'image' : '/themes/waste/theme_image/image_icon',
                        'title' : 'Waste' },
    'freshwater': { 'topic' : 'freshwater quality, water resources',
                        'image' : '/themes/water/theme_image/image_icon',
                        'title' : 'Freshwater' },
    'air pollution': { 'topic' :'air pollution',
                        'image' : '/themes/air/theme_image/image_icon',
                        'title' : 'Air pollution' },
    }

class ReportView(object):
    """ ReportView class
    """
    implements(IReportView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def redirectIfSubReport(self):
        """ Redirect if a subreport is found
        """
        parent = aq_inner(self.context).aq_parent
        if parent.portal_type == self.context.portal_type:
            return self.request.response.redirect('%s#%s' % (
                parent.absolute_url(), self.context.getId()))


    def getTopics(self):
        """ Retrieves the topics of the report
        """
        context = self.context
        parent = aq_inner(self.context).aq_parent
        if parent.portal_type == context.portal_type:
            parent = parent.aq_parent
        while parent.getId() not in ['soer', 'soer-draft'] \
                and parent.portal_type in ['Folder', 'SOERCountry']:
            parent = parent.aq_parent

        topic = context.getTopic()
        result = PARTC_TOPIC_MAP.get(topic, None)
        if result is not None:
            result['url'] = '%s/soer_topic_search?topic=%s' % (
                                        parent.absolute_url(),result['topic'])
            return [result]
        return []

    def getGeoCoverageMapUrl(self):
        """ Get Geo Coverage Map URl
        """
        v =  getUtility(IVocabularyFactory,
                name=u"eea.soer.vocab.NUTSRegions")
        if self.context.getGeoCoverage():
            return u'http://discomap.eea.europa.eu/map/getmap/getMap.aspx?' \
            'layers=0&c=0:ICC:%s:100,20,40&size=300,300&m=http://cow1/ArcGIS/' \
            'services/Internal/EuroBoundaries_Dyna_WM/MapServer' % \
                    v.getCode(self.context.getGeoCoverage())
        else:
            return u'http://discomap.eea.europa.eu/map/getmap/getMap.aspx' \
            '?layers=0&c=0:ICC::100,20,40&size=300,300&m=http://cow1/ArcGIS' \
            '/services/Internal/EuroBoundaries_Dyna_WM/MapServer'

class ReportQuestionsByTopic(object):
    """ Group all reports from a country py a topic and sort them by question.
    """
    implements(IReportQuestionsByTopic)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.topic = self.request.get('topic', None)

    @property
    def topicTitle(self):
        """ Get the title of the topic
        """
        if self.topic == 'country introduction':
            return u'Country profile'
        v = getToolByName(self.context,
                'portal_vocabularies')['eea.soer.vocab.topics']
        if self.topic in v.keys():
            return v[self.topic].Title()
        else:
            return 'Requested topic not found'

    @property
    def reports(self):
        """ Catalog search to get reports based on topic
        """
        context = self.context
        catalog = getToolByName(context, 'portal_catalog')
        query = {'portal_type': ['DiversityReport', 'CommonalityReport'],
                 'sort_on': 'getSoerQuestion',
                 'path': { 'query' : '/'.join(context.getPhysicalPath()),
                           'depth' : 1},
                 }
        if self.topic:
            query['getSoerTopic'] = self.topic
        return catalog(query)

    @property
    def questions(self):
        """ Return a dict with questions from vocab file
        """
        questions = {'DiversityReport': dict([v, k] for k, v in
            vocab.long_diversity_questions.items())}
        questions['CommonalityReport'] = dict([x, y] for x, y in
            vocab.long_questions.items())
        return questions
