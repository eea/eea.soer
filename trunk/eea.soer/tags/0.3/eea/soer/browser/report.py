from zope.interface import implements
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
        
