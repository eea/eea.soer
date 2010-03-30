import surf
from zope.interface import implements
from zope.component import adapts, queryAdapter
from eea.soer.interfaces import IArchetype2Surf
from eea.soer.content.interfaces import ISOERReport
from eea.soer.content.interfaces import ISOERReportingCountry
from Products.ATContentTypes.interface.image import IATImage

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
        NationalStoryClass = session.get_class(surf.ns.SOER['NationalStory'])
        self.resource = NationalStoryClass(self.subject)
        self.resource.session = session
        self.resource.soer_hasFigure = []
        for fig in self.context.objectValues():
            surfObj = queryAdapter(fig, interface=IArchetype2Surf)
            if surfObj is not None:
                self.resource.soer_hasFigure.append(surfObj.save(session))
        self.resource.save()
        return self.resource
        
class Figure2Surf(object):
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
        resource.soer_descriptione = context.Description()
        resource.save()
        return resource
    

