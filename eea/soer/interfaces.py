from zope.interface import Interface


class ISurf2AT(Interface):

    
    def update(context):  #pylint: disable-msg = E0213
        """ updated context with values from RDF """


class INationalStory(ISurf2AT):
    """ marker interface for surf National story """
    
class INationalStory2AT(ISurf2AT):
    """ """

    def getTopic(): #pylint: disable-msg = E0211
        """ return topic from RDF object """        

class ISoerRDF2Surf(Interface):
    """ read a rdf and verify that the feed is correct before content is updated
        in Plone. """

class IReportView(Interface):
    """ report view for templates """

    def redirectIfSubReport():  #pylint: disable-msg = E0211
        """ redirect to the parent report """

    def getTopics():  #pylint: disable-msg = E0211
        """ return links for related topics """

    def getGeoCoverageMapUrl():  #pylint: disable-msg = E0211
        """ return to aut generated map """
        
class ICountryView(Interface):

    def countryIntroduction():  #pylint: disable-msg = E0211
        """ return the 'country introduction' report. It is a DiversityReport with topic 'country introduction' """

    def channel():  #pylint: disable-msg = E0211
        """ return channel info """

    def getMapUrl():  #pylint: disable-msg = E0211
        """ return url to the map """

    def getRegionsUrl(widget):  #pylint: disable-msg = E0213 
        """ return part of a faceted query for geo coverage """
        
class IReportQuestionsByTopic(Interface):

    def topicTitle():  #pylint: disable-msg = E0211
        """ return current topic title """

    def reports():  #pylint: disable-msg = E0211
        """ return a list of reports """

