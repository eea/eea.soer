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

class IReportView(Interface):
    """ report view for templates """

    def redirectIfSubReport():
        """ redirect to the parent report """

    def getTopics():
        """ return links for related topics """

    def getGeoCoverageMapUrl():
        """ return to aut generated map """
        
class ICountryView(Interface):

    def countryIntroduction():
        """ return the 'country introduction' report. It is a DiversityReport with topic 'country introduction' """

    def channel():
        """ return channel info """

    def getMapUrl():
        """ return url to the map """


class IReportQuestionsByTopic(Interface):

    def topicTitle():
        """ return current topic title """

    def reports():
        """ return a list of reports """

