from zope.interface import Interface, Attribute
from zope.schema import Choice, Bool, Set, List, TextLine, Text
from Products.ATContentTypes.interface.folder import IATFolder


class ISOERReport(IATFolder):

    text = Text(
            title=u'Report Content',
            description=u'Content of this report',
            required=True
            )
    
    soerContentType = Choice(
            title=u'Content Type',
            description=u'Which content type are is this?',
            required=True,
            vocabulary=u'SOER Content Types'
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


class ICommonalityReport(ISOERReport):

    soerTopic = List(
            title=u'Topic',
            description=u'Which topic does this report include',
            required=True
            )

    soerSection = Choice(
            title=u'Section',
            description=u'Which report section are you answering to?',
            required=True,
            vocabulary=u'SOER Report Sections',
            )

    short_topic = Attribute("Short version of the selected topic")
    long_section = Attribute("Long version of the selected section")


class IDiversityReport(ISOERReport):

    soerSection = Choice(
            title=u'Section',
            description=u'Which report section are you answering to?',
            required=True,
            vocabulary=u'SOER Diversity Sections',
            )


class IFlexibilityReport(ISOERReport):
    pass
