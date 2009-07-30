from zope.interface import Interface, Attribute
from zope.schema import Choice, Bool, Set, List, Text
from Products.ATContentTypes.interface.folder import IATFolder


class IPossibleSOERContainer(Interface):
    """Marker interface for SOER report containers"""


class ISOERReport(IATFolder):

    text = Text(
            title=u'Topics',
            description=u'Which topics does this report include',
            required=True
            )
    
    topics = List(
            title=u'Topics',
            description=u'Which topics does this report include',
            required=True
            )

    content_type = Choice(
            title=u'Content Type',
            description=u'Which content type are you uploading?',
            required=True,
            vocabulary=u'SOER Content Types'
            )

    sections = Choice(
            title=u'Sections',
            description=u'Which report section are you uploading?',
            required=True,
            vocabulary=u'SOER Report Sections',
            )

    country = Choice(
            title=u'Country',
            description=u'Which country do you represent?',
            required=True,
            vocabulary=u'SOER Report Countries',
            )
