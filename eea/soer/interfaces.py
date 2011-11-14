""" Interfaces
"""
from zope.interface import Interface

class ISurf2AT(Interface):
    """ Surf to AT
    """

    def update(context):
        """ Updated context with values from RDF
        """

class INationalStory(ISurf2AT):
    """ Marker interface for surf National story
    """

class INationalStory2AT(ISurf2AT):
    """ National Story to AT
    """

    def getTopic(self):
        """ Return topic from RDF object
        """

class ISoerRDF2Surf(Interface):
    """ Read a rdf and verify that the feed is correct before content is
        updated in Plone.
    """

class IReportView(Interface):
    """ Report view for templates
    """

    def redirectIfSubReport(self):
        """ Redirect to the parent report
        """

    def getTopics(self):
        """ Return links for related topics
        """

    def getGeoCoverageMapUrl(self):
        """ Return to aut generated map
        """

class ICountryView(Interface):
    """ Country View
    """

    def countryIntroduction(self):
        """ Return the 'country introduction' report. It is a DiversityReport
            with topic 'country introduction'
        """

    def channel(self):
        """ Return channel info
        """

    def getMapUrl(self):
        """ Return url to the map
        """

    def getRegionsUrl(widget):
        """ Return part of a faceted query for geo coverage
        """

class IReportQuestionsByTopic(Interface):
    """  Report Questions By Topic
    """

    def topicTitle(self):
        """ Return current topic title
        """

    def reports(self):
        """ Return a list of reports
        """
