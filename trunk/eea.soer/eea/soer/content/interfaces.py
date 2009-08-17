from zope.interface import Interface, Attribute
from zope.schema import Choice, Bool, Set, List, TextLine, Text
from Products.ATContentTypes.interface.folder import IATFolder


class IPossibleSOERContainer(Interface):
    """Marker interface for SOER report containers"""


class ISOERReport(IATFolder):

    text = Text(
            title=u'Topics',
            description=u'Which topics does this report include',
            required=True
            )
    
    soerTopic = List(
            title=u'Topci',
            description=u'Which topic does this report include',
            required=True
            )

    soerContentType = Choice(
            title=u'Content Type',
            description=u'Which content type are you uploading?',
            required=True,
            vocabulary=u'SOER Content Types'
            )

    soerSection = Choice(
            title=u'Section',
            description=u'Which report section are you uploading?',
            required=True,
            vocabulary=u'SOER Report Sections',
            )

    soerCountry = Choice(
            title=u'Country',
            description=u'Which country do you represent?',
            required=True,
            vocabulary=u'SOER Report Countries',
            )

    soerFeed = TextLine(
            title=u'Feed',
            description=u'RSS feed link',
            required=True,
            )

    short_topic = Attribute("Short version of the selected topic")
    long_section = Attribute("Long version of the selected section")
