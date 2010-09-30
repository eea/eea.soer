import surf
import rdflib
from zope.interface import implements
from zope.component import adapts, queryMultiAdapter
from Products.CMFCore.utils import getToolByName
from eea.soer import vocab
from eea.soer.content.interfaces import ISOERReport, IReportingCountry
from eea.soer.content.interfaces import ISoerFigure, ISoerDataFile
from eea.rdfmarshaller.interfaces import IArchetype2Surf, ISurfSession
from eea.rdfmarshaller import marshaller

class Soer2Surf(marshaller.ATCT2Surf):
    """ base class for adapters """
    prefix= u'soer'
    field_map = {}
    
    @property
    def namespace(self):
        return surf.ns.SOER


class ReportingCountry2Surf(Soer2Surf):
    """ adapter from eea.soer report AT types to surf resource and RDF """
    implements(IArchetype2Surf)
    adapts(IReportingCountry, ISurfSession)

    def channel(self):
        resource = self.session.get_class(self.namespace['Channel'])(self.subject)
        resource.bind_namespaces([self.prefix])
        resource.session = self.session
        language = self.context.Language()
        props = getToolByName(self.context, 'portal_properties').soer_properties
        for propName in ['organisationName', 'organisationURL', 'organisationContactURL', 'organisationLogoURL']:
            value = props.getProperty(propName, None)
            if value is not None:
                setattr(resource, '%s_%s' % (self.prefix, propName), (value, language))
                
        # rdf:resource values
        for propName in ['license']:                
            value = props.getProperty(propName, None)
            if value is not None:
                setattr(resource, '%s_%s' % (self.prefix, propName), rdflib.URIRef(value))

        resource.save()
        return resource
            
    def at2surf(self, **kwargs):
        self.channel()
        for obj in self.context.objectValues():
            atsurf = queryMultiAdapter((obj, self.session), interface=IArchetype2Surf)
            if atsurf is not None:
                atsurf.at2surf()
                
class NationalStory2Surf(Soer2Surf):
    """ adapter from eea.soer report AT types to surf resource and RDF """
    implements(IArchetype2Surf)
    adapts(ISOERReport, ISurfSession)

    portalType = 'NationalStory'

    def __init__(self, context, session):
        super(NationalStory2Surf, self).__init__(context, session)
        self.field_map = dict([('text', 'assessment'),
                      ('subject', 'keyword'),
                      ('modification_date', 'modified'),
                      ('effectiveDate','pubDate'),
                      ])

    @property
    def blacklist_map(self):
        return super(NationalStory2Surf, self).blacklist_map + ['relatedItems', 'question', 'geoCoverage', 'id']
    
    def at2surf(self, subReport=False, **kwargs):
        resource = super(NationalStory2Surf, self).at2surf()
        context = self.context
        language = context.Language()
        question = context.getQuestion()
        if context.portal_type == 'DiversityReport':
            question = vocab.long_diversity_questions[context.getQuestion()]
        elif context.portal_type == 'CommonalityReport':
            question = vocab.long_questions[context.getQuestion()]
        resource.soer_question = (question, language)
        resource.soer_geoCoverage = rdflib.URIRef(context.getGeoCoverage())
        resource.soer_hasFigure = []
        if subReport:
            resource.soer_sortOrder = context.aq_parent.getObjectPosition(context.getId()) + 1
        for obj in context.objectValues():
            surfObj = queryMultiAdapter((obj,self.session), interface=IArchetype2Surf)
            if surfObj is not None:
                if obj.portal_type == 'Image':
                    resource.soer_hasFigure.append(surfObj.at2surf())
                elif obj.portal_type in ['DataSourceLink', 'Link']:
                    # we allowed normal links as data source pre 0.5
                    resource.soer_dataSource.append(surfObj.at2surf())
                elif obj.portal_type == 'RelatedIndicatorLink':
                    resource.soer_relatedEuropeanIndicator.append((rdflib.URIRef(obj.getRemoteUrl()), language))
                else:
                    # current resource has the sort order 0 since it is parent to the other reports
                    resource.soer_sortOrder = 0
                    surfObj.at2surf(subReport=True)
        
            
        
        resource.save()
        return resource

class Image2Surf(Soer2Surf):
    """ Resource axtension for """
    implements(IArchetype2Surf)
    adapts(ISoerFigure, ISurfSession)

    portalType = u'Figure'

    def __init__(self, context, session):
        super(Image2Surf, self).__init__(context, session)
        self.field_map.update( dict([('id', 'fileName'),
                                     ('title', 'caption'),
                                     ('relatedItems', 'dataSource'),
                                     ]))
        self.dc_map = {} # we don't want Dublin Core right now
        


class Link2Surf(Soer2Surf):
    """ Resource axtension for """
    implements(IArchetype2Surf)
    adapts(ISoerDataFile, ISurfSession)

    portalType = u'DataFile'
    
    def __init__(self, context, session):
        super(Link2Surf, self).__init__(context, session)
        self.field_map.update( dict([('id', 'fileName'),
                                     ('remoteUrl', 'dataURL'),
                                     ]))
        self.dc_map = {} # we don't want Dublin Core right now

    @property
    def blacklist_map(self):
        return  super(Link2Surf, self).blacklist_map + Soer2Surf.dc_map.keys()
