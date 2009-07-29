from zope.interface import Interface, Attribute
from zope.schema import Choice, Bool, Set, List
from Products.ATContentTypes.interface.folder import IATFolder


class IPossibleSOERContainer(Interface):
    """Marker interface for SOER report containers"""


class ISOERReport(IATFolder):
    
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

    contry = Choice(
            title=u'Country',
            description=u'Which country do you represent?',
            required=True,
            vocabulary=u'SOER Report Countries',
            )
