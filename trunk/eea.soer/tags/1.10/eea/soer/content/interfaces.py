from zope.interface import Interface, Attribute
from zope.schema import Choice, Bool, Set, List, TextLine, Text


class ISOERReport(Interface):

    reportingCountryCode = Attribute(u'Which country do you represent?')

    geoCoverage = Choice(
            title=u'Geographical coverage',
            description=u'The geographical (spatial) area covered by the assessment.',
            required=True,
            vocabulary=u'Geographical coverage'
            )

    topic = List(
            title=u'Topic',
            description=u'Which topic does this report include',
            required=True
            )

    question = Choice(
            title=u'Question',
            description=u'Which report section are you answering to?',
            required=True,
            vocabulary=u'SOER Questions'
            )

    short_topic = Attribute("Short version of the selected topic")
    long_section = Attribute("Long version of the selected section")

    description = Text(
            title=u'Key message',
            description=u'This is a short key message for the National Story, a kind of very short summary or teaser (one/two paragraphs)',
            required=True
            )

    # keyMessage
    keyMessage = Text(
            title=u'Key message',
            description=u'This is a short key message for the National Story, a kind of very short summary or teaser (one/two paragraphs)',
            required=True
            )

    #assesment
    assessment = Text(
            title=u'Report assesment',
            description=u'Content of this report',
            required=True
            )
    
    

class ICommonalityReport(ISOERReport):
    pass

class IDiversityReport(ISOERReport):
    pass

class IFlexibilityReport(ISOERReport):
    pass


class IReportingCountry(Interface):
    """ For a folder that contains SOER reports.
        This interface is then used to create RDF from that folder for all
        contained reports. """

    def updateFromFeed():
        """ Update reports from the rdf feed url """
    

class ISoerFigure(Interface):
    """ Marker interface for Images inside a SOER report """

class ISoerDataFile(Interface):
    """ Marker interface for Links inside a SOER report """

