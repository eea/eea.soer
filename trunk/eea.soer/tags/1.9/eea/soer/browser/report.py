from zope.interface import implements
from zope.component import getUtility, queryMultiAdapter
from zope.app.schema.vocabulary import IVocabularyFactory
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
    """ """
    implements(IReportView)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def redirectIfSubReport(self):
        parent = aq_inner(self.context).aq_parent
        if parent.portal_type == self.context.portal_type:
            return self.request.response.redirect('%s#%s' % (parent.absolute_url(), self.context.getId()))
        
    
    def getTopics(self):
        context = self.context
        parent = aq_inner(self.context).aq_parent
        if parent.portal_type == context.portal_type:
            parent = parent.aq_parent
        while parent.getId() not in ['soer', 'soer-draft'] and parent.portal_type in ['Folder', 'SOERCountry']:
            parent = parent.aq_parent
        
        topic = context.getTopic()
        result = PARTC_TOPIC_MAP.get(topic, None)
        if result is not None:
            result['url'] = '%s/soer_topic_search?topic=%s' % (parent.absolute_url(),result['topic'])
            return [result]
        return []

    def getGeoCoverageMapUrl(self):
        vocab =  getUtility(IVocabularyFactory, name=u"eea.soer.vocab.NUTSRegions")
        if self.context.getGeoCoverage():
            return u'http://discomap.eea.europa.eu/map/getmap/getMap.aspx?layers=0&c=0:ICC:%s:100,20,40&size=300,300&m=http://cow1/ArcGIS/services/Internal/EuroBoundaries_Dyna_WM/MapServer' % vocab.getCode(self.context.getGeoCoverage())
        else:
            return u'http://discomap.eea.europa.eu/map/getmap/getMap.aspx?layers=0&c=0:ICC::100,20,40&size=300,300&m=http://cow1/ArcGIS/services/Internal/EuroBoundaries_Dyna_WM/MapServer'
    

class ReportQuestionsByTopic(object):
    """ Group all reports from a country py a topic and sort them by question."""

    implements(IReportQuestionsByTopic)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.topic = self.request.get('topic')

    @property
    def topicTitle(self):
        if self.topic == 'country introduction':
            return u'Country profile'
        vocab = getToolByName(self.context, 'portal_vocabularies')['eea.soer.vocab.topics']
        return vocab[self.topic].Title()
    
    @property
    def reports(self):
        """ """
        context = self.context
        catalog = getToolByName(context, 'portal_catalog')
        query = {'portal_type' : ['DiversityReport', 'CommonalityReport'],
                 'getSoerTopic' : self.topic,
                 'sort_on' : 'getSoerQuestion',
                 'path' : { 'query' : '/'.join(context.getPhysicalPath()),
                            'depth' : 1},
                 }
        return catalog(query)
            
    @property
    def questions(self):
        questions = { 'DiversityReport' : dict([[v,k] for k,v in vocab.long_diversity_questions.items()]) }
        questions['CommonalityReport'] = dict([[v,k] for k,v in vocab.long_questions.items()])
        return questions

