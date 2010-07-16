from zope.interface import implements
from zope.component import getUtility, queryMultiAdapter
from zope.app.schema.vocabulary import IVocabularyFactory
from eea.soer.interfaces import IReportView
from Acquisition import aq_inner

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
        return u'http://map.eea.europa.eu/getmap.asp?Fullextent=1&imagetype=3&size=W600&PredefShade=GreenRed&Q=%s:2' % vocab.getCode(self.context.getGeoCoverage())
    
