""" Sense module
"""
from Products.Marshall.registry import getComponent

class RDFExport(object):
    """ RDFExport class
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        marshaller = getComponent('surfrdf')
        _content_type, _length, data = marshaller.marshall(self.context)
        self.request.response.setHeader(
                'Content-Type','application/rdf+xml; charset=utf-8')
        return data

class ChannelInfo(object):
    """ ChannelInfo class
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ Return channel info
        """
        pass

