from Products.Marshall.registry import getComponent


class RDFExport(object):
    """ """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        marshaller = getComponent('surfrdf')
        content_type, length, data = marshaller.marshall(self.context)
        self.request.response.setHeader('Content-Disposition',
                 'attachment; filename="sense-%s.rdf"' % self.context.getId())
        return data
