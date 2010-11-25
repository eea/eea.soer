import surf
import rdflib
from zope.interface import implements
from zope.component import adapts
from eea.soer import vocab
from eea.soer.interfaces import ISoerRDF2Surf, INationalStory
from eea.soer.content import SOERReport
from eea.soer.content.interfaces import ISOERReport
from DateTime import DateTime
from Products.Archetypes import interfaces as atinterfaces
from Products.CMFPlone import log

def getSingleValue(value, language=u"en"):
    for v in value:
        if isinstance(v, rdflib.Literal) and v.language == language:
            return v
    return value.first or ''


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
        # old labels before https://svn.eionet.europa.eu/projects/Zope/ticket/3685
        questions.update(dict([[v,k] for k,v in vocab.old_long_questions.items()]))            
        
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
                  'subject' : 'keyword',
                  'modification_date' : 'modified'}
    
    def __init__(self, context):
        self.context = context
        self._updateFromSurf()
        
    def _updateFromSurf(self):
        context = self.context
        for fname in  atinterfaces.ISchema(context).fieldNames():
            fname = self.index_map.get(fname, fname)
            field = getattr(context, 'soer_%s' % fname)
            if fname == 'description' and not field.first:
                # no or empty soer description, fall back to DC
                field = getattr(context, 'dc_description')
                if not field.first:
                    field = getattr(context, 'dc_Description')
            if fname in ['keyword']:
                setattr(self, fname, [ value.strip().encode('utf8') for value in field ])
            elif field.first is not None:
                setattr(self, fname, field.first.strip().encode('utf8'))
            else:
                setattr(self, fname, '')
        setattr(self, 'subject', context.subject)
        sortOrder = context.soer_sortOrder.first
        if sortOrder is not None:
            setattr(self, 'sortOrder', sortOrder.strip())
        self.topic = self.topic.lower()
        
    @property
    def portal_type(self):
        portal_type = 'FlexibilityReport'
        if self.topic == 'country introduction':
            portal_type = 'DiversityReport'                                            
        elif self.topic.decode('utf8') in vocab.long_topics.keys():
            if self.question.decode('utf8') in vocab.long_questions.values() + vocab.old_long_questions.values():
                portal_type = 'CommonalityReport'
            elif self.question.decode('utf8') in vocab.long_diversity_questions.values() + vocab.old_long_diversity_questions.values():
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
                sortOrder = 0
                if hasattr(fig, 'soer_sortOrder'):
                    if fig.soer_sortOrder.first is not None:
                        sortOrder = int(str(fig.soer_sortOrder.first))
                result =  { 'url' : fig.subject.strip(),
                            'fileName' : fileName,
                            'caption' : str(fig.soer_caption.first),
                            'description' : str(fig.soer_description.first),
                            'sortOrder' :  sortOrder }

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

class SoerRDF2Surf(object):
    """ read a rdf and verify that the feed is correct before content is updated
        in Plone. """
    implements(ISoerRDF2Surf)
    
    def __init__(self, url):
        self.store = surf.Store(reader='rdflib',  writer='rdflib', rdflib_store = 'IOMemory')
        self.session = surf.Session(self.store, mapping={surf.ns.SOER.NationalStory : NationalStory} )
        self.store.load_triples(source=url)        

    def channel(self):
        channel = self.session.get_class(surf.ns.SOER['Channel']).all()
        if not channel:
            channel = self.session.get_class(surf.ns.SOER['channel']).all()
        if channel:
            channel = channel.one()
            result ={'organisationName' : getSingleValue(channel.soer_organisationName),
                      'organisationURL'  : getSingleValue(channel.soer_organisationURL),
                      'organisationContactURL'  : getSingleValue(channel.soer_organisationContactURL),
                      'organisationLogoURL' : getSingleValue(channel.soer_organisationLogoURL),
                      'license' : getSingleValue(channel.soer_license),
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
