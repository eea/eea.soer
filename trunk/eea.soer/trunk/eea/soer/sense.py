import surf
import rdflib
from zope.interface import implements
from zope.component import adapts, queryMultiAdapter
from eea.soer import vocab
from eea.soer.interfaces import ISoerRDF2Surf, INationalStory
from eea.soer.content.interfaces import ISOERReport, IReportingCountry
from eea.soer.content import SOERReport
from DateTime import DateTime
from Products.Archetypes import interfaces as atinterfaces
from Products.ATContentTypes.interface.image import IATImage
from Products.ATContentTypes.interface.link import IATLink
from Products.CMFPlone import log
from eea.rdfmarshaller.interfaces import IArchetype2Surf, ISurfSession
from eea.rdfmarshaller import marshaller

class GetATSchema4SurfObj(object):
    implements(atinterfaces.ISchema)
    adapts(INationalStory)
    
    def __init__(self, context):
        self.context = context

    @property
    def schema(self):
        return SOERReport.schema

    def fieldNames(self):
        return [field.getName() for field in self.schema.fields() ] + ['relatedEuropeanIndicator']

class Soer2Surf(marshaller.ATCT2Surf):
    """ base class for adapters """
    prefix= u'soer'

    @property
    def namespace(self):
        return surf.ns.SOER


class ReportingCountry2Surf(Soer2Surf):
    """ adapter from eea.soer report AT types to surf resource and RDF """
    implements(IArchetype2Surf)
    adapts(IReportingCountry, ISurfSession)

    def at2surf(self):
        super(ReportingCountry2Surf, self).at2surf()
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
                      ])
        self.blacklist_map = Soer2Surf.blacklist_map + [key for key in Soer2Surf.dc_map.keys()] + ['relatedItems', 'question', 'geoCoverage', 'id']
    
    def at2surf(self):
        resource = super(NationalStory2Surf, self).at2surf()
        context = self.context
        question = context.getQuestion()
        if context.portal_type == 'DiversityReport':
            question = vocab.long_diversity_questions[context.getQuestion()]
        elif context.portal_type == 'CommonalityReport':
            question = vocab.long_questions[context.getQuestion()]
        resource.soer_question = question
        resource.soer_geoCoverage = rdflib.URIRef(context.getGeoCoverage())
        resource.soer_hasFigure = []
        for obj in context.objectValues():
            surfObj = queryMultiAdapter((obj,self.session), interface=IArchetype2Surf)
            if surfObj is not None:
                if obj.portal_type == 'Image':
                    resource.soer_hasFigure.append(surfObj.at2surf())
                elif obj.portal_type == 'Link':
                    resource.soer_dataSource.append(surfObj.at2surf())
                elif obj.portal_type == 'RelatedIndicatorLink':
                    resource.soer_relatedEuropeanIndicator.append(rdflib.URIRef(obj.getRemoteUrl()))
                else:
                    surfObj.at2surf()
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
                  'effectiveDate' : 'pubDate',
                  'subject' : 'keyword'}
    
    def __init__(self, context):
        self.context = context
        self._updateFromSurf()
        
    def _updateFromSurf(self):
        context = self.context
        for fname in  atinterfaces.ISchema(context).fieldNames():
            fname = self.index_map.get(fname, fname)
            field = getattr(context, 'soer_%s' % fname)
            if fname in ['keyword']:
                setattr(self, fname, [ value.strip().encode('utf8') for value in field ])
            elif field.first is not None:
                setattr(self, fname, field.first.strip().encode('utf8'))
            else:
                setattr(self, fname, '')
        setattr(self, 'subject', context.subject)
        
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
            i = 0
            for fig in context.soer_hasFigure:
                try:
                    fileName = fig.soer_fileName.first and str(fig.soer_fileName.first) or 'tempfile'
                except:
                    log.log('Figure resource without information %s' % fig, severity=log.logging.WARN)
                    continue
                
                result =  { 'url' : fig.subject.strip(),
                            'fileName' : fileName,
                            'caption' : str(fig.soer_caption.first),
                            'description' : str(fig.soer_description.first) }

                if fig.soer_mediaType.first is not None:
                    result['mediaType'] = fig.soer_mediaType.first.strip()
                if fig.soer_dataSource.first is not None:
                    dataSrc = fig.soer_dataSource.first
                    if not isinstance(dataSrc, rdflib.URIRef):
                        fileName = dataSrc.soer_fileName.first and str(dataSrc.soer_fileName.first) or 'tempfile'
                        result['dataSource'] = { 'url' : dataSrc.subject.strip(),
                                                 'fileName' : fileName,
                                                 'dataURL' : dataSrc.soer_dataURL.first.strip() }
                    else:
                        result['dataSource'] = { 'url' : str(dataSrc),
                                                 'fileName' : fileName,
                                                 'dataURL' : str(dataSrc) }
                        log.log('Data source without information %s' % dataSrc, severity=log.logging.WARN)
                                                 
                yield result
                        
    def dataSource(self):
        context = self.context
        if context.soer_dataSource:
            for dataSrc in context.soer_dataSource:
                yield { 'url' : dataSrc.subject.strip(),
                        'fileName' : dataSrc.soer_fileName.first.strip(),
                        'dataURL' : dataSrc.soer_dataURL.first.strip() }

    def relatedIndicator(self):
        context = self.context
        if context.soer_relatedEuropeanIndicator:
            return [ str(indicator) for indicator in context.soer_relatedEuropeanIndicator ]
        return []
                
class Image2Surf(Soer2Surf):
    """ Resource axtension for """
    implements(IArchetype2Surf)
    adapts(IATImage, ISurfSession)

    portalType = u'Figure'

    def __init__(self, context, session):
        super(Image2Surf, self).__init__(context, session)
        self.field_map = Soer2Surf.field_map
        self.field_map.update( dict([('id', 'fileName'),
                                     ('title', 'caption'),
                                     ('relatedItems', 'dataSource'),
                                     ]))
        self.blacklist_map = Soer2Surf.blacklist_map + [key for key in Soer2Surf.dc_map.keys()
                                          if key not in ('title', 'description')]  + ['relatedItems','image']
        self.dc_map = {} # we don't want Dublin Core right now

    

class Link2Surf(Soer2Surf):
    """ Resource axtension for """
    implements(IArchetype2Surf)
    adapts(IATLink, ISurfSession)

    portalType = u'DataFile'
    
    def __init__(self, context, session):
        super(Link2Surf, self).__init__(context, session)
        self.field_map = Soer2Surf.field_map
        self.field_map.update( dict([('id', 'fileName'),
                                     ('remoteUrl', 'dataURL'),
                                     ]))
        self.blacklist_map = Soer2Surf.blacklist_map + Soer2Surf.dc_map.keys()
        self.dc_map = {} # we don't want Dublin Core right now


class SoerRDF2Surf(object):
    """ read a rdf and verify that the feed is correct before content is updated
        in Plone. """
    implements(ISoerRDF2Surf)
    
    def __init__(self, url):
        self.store = surf.Store(reader='rdflib',  writer='rdflib', rdflib_store = 'IOMemory')
        self.session = surf.Session(self.store, mapping={surf.ns.SOER.NationalStory : NationalStory} )
        self.store.load_triples(source=url)        

    def channel(self):
        channel = self.session.get_class(surf.ns.SOER['channel']).all()
        if channel:
            channel = channel.one()
            result = {'organisationName' : channel.soer_organisationName.first.strip(),
                      'organisationURL'  : channel.soer_organisationURL.first.strip(),
                      'organisationContactURL'  : channel.soer_organisationContactURL.first.strip(),
                      'organisationLogoURL' : channel.soer_organisationLogoURL.first.strip(),
                      'license' : channel.soer_license.first.strip(),
                      'updated' : DateTime() }
            return result
    
    def nationalStories(self):
        NationalStory = self.session.get_class(surf.ns.SOER['NationalStory'])
        for nstory in NationalStory.all().order():
            yield ISOERReport(nstory)

    nsFormating = "\n%s\n%20s %6s %9s %5s %7s %8s %8s %10s %6s %5s\n"
    figFormating = "%s\n%20s %6s %9s %5s %7s\n"
    def status(self):
        result = ""
        NationalStory = self.session.get_class(surf.ns.SOER['NationalStory'])
        DataFile = self.session.get_class(surf.ns.SOER['DataFile'])
        result += self.nsFormating % (' ',' ', 'Topic','Question', 'Desc','KeyMsg','Assesment','KeyWord','Indicator','Figure','Data')
        for nstory in NationalStory.all().order():
            nstory = ISOERReport(nstory)
            result += self._checkNationalStory(nstory)
            for fig in nstory.hasFigure():
                result += self._checkFigure(fig)
                if fig['dataSource']:
                    result += self._checkDataSource(fig['dataSource'])
            for dataSrc in nstory.dataSource():
                result += self._checkDataSource(dataSrc)
                
        return result

    def _checkChannel(self, channel):
        pass
    
    def _checkNationalStory(self, nstory):
        subjectSize = len(nstory.subject)
        if subjectSize > 20:
            subject = nstory.subject[subjectSize-20:]
        result = self.nsFormating % ( nstory.subject,
                                    'NationalStory',
                                    chk(nstory.topic),
                                    chk(nstory.question),
                                    chk(nstory.description),
                                    chk(nstory.keyMessage),
                                    chk(nstory.assessment),
                                    chk(nstory.keyword),
                                    chk(nstory.relatedEuropeanIndicator),
                                    chk(nstory.hasFigure),
                                    chk(nstory.dataSource)
                                    )
        return result

    def _checkFigure(self, fig):
        subjectSize = len(fig['url'])
        if subjectSize > 20:
            subject = fig['url'][subjectSize-20:]
        result = self.figFormating % (fig['url'],
                                      'Figure',
                                    chk(fig['mediaType']),
                                    chk(fig['caption']),
                                    chk(fig['description']),
                                    chk(fig['dataSource'])
                                    )
        return result
    
    def _checkDataSource(self, dataSrc):
        subjectSize = len(dataSrc['url'])
        if subjectSize > 20:
            subject = dataSrc['url'][subjectSize-20:]
        result = self.figFormating % (dataSrc['url'],
                                      'DataSource','','',
                                    chk(dataSrc['fileName']),
                                    chk(dataSrc['dataURL'])
                                    )
        return result


    


def chk(context):
    return context and 'OK' or 'Miss'
