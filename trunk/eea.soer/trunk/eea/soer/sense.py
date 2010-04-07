import surf
from zope.interface import implements
from zope.component import adapts, queryAdapter
from eea.soer import vocab
from eea.soer.interfaces import IArchetype2Surf
from eea.soer.content.interfaces import ISOERReport
from eea.soer.content.interfaces import ISOERReportingCountry
from Products.ATContentTypes.interface.image import IATImage
from Products.ATContentTypes.interface.link import IATLink

class Archetype2Surf(object):

    def at2surf(self, context):
        context.at2Surf()

class NationalStory2Surf(object):
    """ adapter from eea.soer report AT types to surf resource and RDF """
    implements(IArchetype2Surf)
    adapts(ISOERReport)

    def __init__(self, context):
        self.context = context

    @property
    def subject(self):
        return self.context.absolute_url()
        
    def save(self, session):
        context = self.context
        NationalStoryClass = session.get_class(surf.ns.SOER['NationalStory'])
        resource = NationalStoryClass(self.subject)
        resource.session = session
        question = context.getSoerQuestion()
        if context.portal_type == 'DiversityReport':
            question = vocab.long_diversity_questions[context.getSoerQuestion()]
        elif context.portal_type == 'CommonalityReport':
            question = vocab.long_questions[context.getSoerQuestion()]
        resource.soer_question = question
        resource.soer_keyMessage = context.Description()
        resource.soer_geoCoverage = context.getGeoCoverage()
        resource.soer_topic = context.getSoerTopic()
        resource.soer_assessment = context.getText()
        resource.soer_hasFigure = []
        for fig in context.objectValues():
            surfObj = queryAdapter(fig, interface=IArchetype2Surf)
            if surfObj is not None:
                if fig.portal_type == 'Image':
                    resource.soer_hasFigure.append(surfObj.save(session))
                elif fig.portal_type == 'Link':
                    resource.soer_dataSource.append(surfObj.save(session))
        resource.save()
        return resource
        
class Image2Surf(object):
    """ Resource axtension for """
    implements(IArchetype2Surf)
    adapts(IATImage)

    def __init__(self, context):
        self.context = context
    
    @property
    def subject(self):
        return self.context.absolute_url()

    def save(self, session):
        context = self.context
        FigureClass = session.get_class(surf.ns.SOER['Figure'])
        resource = FigureClass(self.subject)
        resource.session = session
        resource.soer_fileName = self.context.getId()
        resource.soer_capiton = context.Title()
        resource.soer_description = context.Description()
        resource.soer_dataSource = []
        for dataFile in context.getRelatedItems():
            resource.soer_dataSource.append(dataFile.absolute_url())
        resource.save()
        return resource
    

class Link2Surf(object):
    """ Resource axtension for """
    implements(IArchetype2Surf)
    adapts(IATLink)

    def __init__(self, context):
        self.context = context
    
    @property
    def subject(self):
        return self.context.absolute_url()

    def save(self, session):
        context = self.context
        DataFileClass = session.get_class(surf.ns.SOER['DataFile'])
        resource = DataFileClass(self.subject)
        resource.session = session
        resource.soer_fileName = self.context.getId()
        resource.save()
        return resource
    
