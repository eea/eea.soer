import surf
import rdflib
from zope.interface import implements
from zope.component import adapts, queryMultiAdapter
from zope import schema
from eea.soer import vocab
from eea.soer.interfaces import ISoerRDF2Surf, INationalStory
from eea.soer.content.interfaces import ISOERReport, IReportingCountry
from eea.soer.content import SOERReport
from DateTime import DateTime
from Products.Archetypes import interfaces as atinterfaces
from Products.ATContentTypes.interface.image import IATImage
from Products.ATContentTypes.interface.link import IATLink
from eea.rdfmarshaller.interfaces import IArchetype2Surf, ISurfSession

class GetATSchema4SurfObj(object):
    implements(atinterfaces.ISchema)
    adapts(INationalStory)
    
    def __init__(self, context):
        self.context = context

    @property
    def schema(self):
        return SOERReport.schema

    def fieldNames(self):
        for field in self.schema.fields():
            yield field.getName()
            

class ReportingCountry2Surf(object):
    """ adapter from eea.soer report AT types to surf resource and RDF """
    implements(IArchetype2Surf)
    adapts(IReportingCountry, ISurfSession)


    def __init__(self, context, session):
        self.context = context
        self.session = session
        
    @property
    def namespace(self):
        return surf.ns.SOER

    @property
    def prefix(self):
        return ''
    
    def at2surf(self):
        for obj in self.context.objectValues():
            atsurf = queryMultiAdapter((obj, self.session), interface=IArchetype2Surf)
            atsurf.at2surf()
        
class NationalStory2Surf(object):
    """ adapter from eea.soer report AT types to surf resource and RDF """
    implements(IArchetype2Surf)
    adapts(ISOERReport, ISurfSession)

    def __init__(self, context, session):
        self.context = context
        self.session = session
        
    @property
    def namespace(self):
        return surf.ns.SOER

    @property
    def prefix(self):
        return 'soer'
    
    @property
    def subject(self):
        return self.context.absolute_url()

    def at2surf(self):
        context = self.context
        session = self.session
        NationalStoryClass = session.get_class(surf.ns.SOER['NationalStory'])
        resource = NationalStoryClass(self.subject)
        resource.session = session
        question = context.getQuestion()
        if context.portal_type == 'DiversityReport':
            question = vocab.long_diversity_questions[context.getQuestion()]
        elif context.portal_type == 'CommonalityReport':
            question = vocab.long_questions[context.getQuestion()]
        resource.soer_question = question
        resource.soer_description = context.Description()
        resource.soer_keyMessage = context.getKeyMessage()
        resource.soer_geoCoverage = rdflib.URIRef(context.getGeoCoverage())
        resource.soer_topic = context.getTopic()
        resource.soer_assessment = context.getText()
        resource.soer_hasFigure = []
        for fig in context.objectValues():
            surfObj = queryMultiAdapter((fig,session), interface=IArchetype2Surf)
            if surfObj is not None:
                if fig.portal_type == 'Image':
                    resource.soer_hasFigure.append(surfObj.at2surf())
                elif fig.portal_type == 'Link':
                    resource.soer_dataSource.append(surfObj.at2surf())
        resource.save()
        return resource

class NationalStory(object):
    implements(INationalStory)
    

    @property
    def effectiveDate(self):
        return DateTime(self.soer_pubDate.first.strip())

    @property
    def modified(self):
        return DateTime(self.soer_modified.first.strip())

    def update(self, country):
        questions = dict([[v,k] for k,v in vocab.long_diversity_questions.items()])
        questions.update(dict([[v,k] for k,v in vocab.long_questions.items()]))
        
        report = country[country.invokeFactory(self.portal_type, id='temp_report',
                                         soerTopic=self.getTopic(),
                                         soerQuestion=questions[self.question])]
        if self.soer_assessment.first is not None:
            report.setText(self.soer_assessment.first.strip())
        else:
            # log missing assesment
            pass


class Surf2SOERReport(object):
    implements(ISOERReport)
    adapts(INationalStory)

    index_map = { 'text' : 'assessment',
                  'effective' : 'pubDate'}
    
    def __init__(self, context):
        self.context = context
        self._updateFromSurf()
        
    def _updateFromSurf(self):
        context = self.context
        for fname in  atinterfaces.ISchema(context).fieldNames():
            fname = self.index_map.get(fname, fname)
            field = getattr(context, 'soer_%s' % fname)
            if field.first is not None:
                setattr(self, fname, field.first.strip().encode('utf8'))
            else:
                setattr(self, fname, '')
    @property
    def portal_type(self):
        portal_type = 'FlexibilityReport'
        if self.topic == u'country introduction':
            portal_type = 'DiversityReport'                                            
        elif self.topic in [u'air pollution', u'freshwater', u'climate change',
                            u'land', u'waste', u'biodiversity']:
            if self.question in vocab.long_questions.values():
                portal_type = 'CommonalityReport'
            elif self.question in vocab.long_diversity_questions.values():
                portal_type = 'DiversityReport'                        
        return portal_type

    def hasFigure(self):
        context = self.context
        if context.soer_hasFigure:
            for fig in context.soer_hasFigure:
                try:
                    yield { 'url' : fig.subject.strip(),
                            'fileName' : fig.soer_fileName.first.strip(),
                            'caption' : fig.soer_caption.first.strip(),
                            'description' : fig.soer_description.first.strip() }
                except:
                    continue
                        
        
class Image2Surf(object):
    """ Resource axtension for """
    implements(IArchetype2Surf)
    adapts(IATImage, ISurfSession)

    def __init__(self, context, session):
        self.context = context
        self.session = session
    
    @property
    def subject(self):
        return self.context.absolute_url()

    def at2surf(self):
        context = self.context
        session = self.session
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
    adapts(IATLink, ISurfSession)

    def __init__(self, context, session):
        self.context = context
        self.session = session
    
    @property
    def subject(self):
        return self.context.absolute_url()

    def at2surf(self):
        context = self.context
        session = self.session
        DataFileClass = session.get_class(surf.ns.SOER['DataFile'])
        resource = DataFileClass(self.subject)
        resource.session = session
        resource.soer_fileName = self.context.getId()
        resource.save()
        return resource
    

class SoerRDF2Surf(object):
    """ read a rdf and verify that the feed is correct before content is updated
        in Plone. """
    implements(ISoerRDF2Surf)
    
    def __init__(self, url):
        self.store = surf.Store(reader='rdflib',  writer='rdflib', rdflib_store = 'IOMemory')
        self.session = surf.Session(self.store, mapping={surf.ns.SOER.NationalStory : NationalStory} )
        self.store.load_triples(source=url)        

    def nationalStories(self):
        NationalStory = self.session.get_class(surf.ns.SOER['NationalStory'])
        for nstory in NationalStory.all():
            yield ISOERReport(nstory)
