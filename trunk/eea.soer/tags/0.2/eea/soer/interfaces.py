from zope.interface import Interface


class ISurf2AT(Interface):

    
    def update(context):
        """ updated context with values from RDF """


class INationalStory(ISurf2AT):
    """ marker interface for surf National story """
    
class INationalStory2AT(ISurf2AT):
    """ """

    def getTopic():
        """ return topic from RDF object """        

class ISoerRDF2Surf(Interface):
    """ read a rdf and verify that the feed is correct before content is updated
        in Plone. """
