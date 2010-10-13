from zope.interface import implements
from zope.component import getUtility, queryMultiAdapter
from zope.app.schema.vocabulary import IVocabularyFactory
from eea.soer.interfaces import IReportView, IReportQuestionsByTopic
from eea.soer import vocab
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

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
        topic = context.getTopic()
        adapter = queryMultiAdapter((context, self.request), name=u'themes-object', default=None)
        themes = []
        if adapter is not None:
            themes = adapter.short_items()
        return themes


    def getGeoCoverageMapUrl(self):
        vocab =  getUtility(IVocabularyFactory, name=u"eea.soer.vocab.NUTSRegions")
        if self.context.getGeoCoverage():
            return u'http://map.eea.europa.eu/getmap.asp?Fullextent=1&imagetype=3&size=W600&PredefShade=GreenRed&Q=%s:2' % vocab.getCode(self.context.getGeoCoverage())
        else:
            return u'http://map.eea.europa.eu/getmap.asp?Fullextent=1&imagetype=3&size=W600&PredefShade=GreenRed'
    

class ReportQuestionsByTopic(object):
    """ Group all reports from a country py a topic and sort them by question."""

    implements(IReportQuestionsByTopic)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.topic = self.request.get('topic')

    @property
    def topicTitle(self):
        vocab = getToolByName(self.context, 'portal_vocabularies')['eea.soer.vocab.topics']
        return vocab[self.topic].Title()
    
    @property
    def reports(self):
        """ """
        context = self.context
        catalog = getToolByName(context, 'portal_catalog')
        query = {'portal_type' : ['DiversityReport', 'CommonalityReport'],
                 'getSoerCountry' : context.getId(),
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

