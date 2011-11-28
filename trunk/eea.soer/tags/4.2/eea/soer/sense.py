""" Sense
"""
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
import logging

def getSingleValue(value, language=u"en"):
    """ Get single value
    """
    for v in value:
        if isinstance(v, rdflib.Literal) and v.language == language:
            return v
    return value.first or ''

class GetATSchema4SurfObj(object):
    """ Get AT Schema for Surf Obj
    """
    implements(atinterfaces.ISchema)
    adapts(INationalStory)

    def __init__(self, context):
        self.context = context

    @property
    def schema(self):
        """ Schema
        """
        return SOERReport.schema

    def fieldNames(self):
        """ Field names
        """
        return [field.getName() for field in
                         self.schema.fields() ] + ['relatedEuropeanIndicator']

class NationalStory(object):
    """ National Story
    """
    implements(INationalStory)

    @property
    def effectiveDate(self):
        """ Effective Date
        """
        return DateTime(self.soer_pubDate.first.strip())

    @property
    def modified(self):
        """ Modified
        """
        return DateTime(self.soer_modified.first.strip())

    def update(self, country):
        """ Update
        """
        questions = dict([v, k] for k, v in
                                    vocab.long_diversity_questions.items())
        questions.update(dict([x, y] for x, y in
                                    vocab.long_questions.items()))
        # Old labels before #3685
        questions.update(dict([m, n] for m, n in
                                    vocab.old_long_questions.items()))

        report = country[country.invokeFactory(
                                      self.portal_type, id='temp_report',
                                      soerTopic=self.getTopic(),
                                      soerQuestion=questions[self.question])]
        if self.soer_assessment.first is not None:
            report.setText(self.soer_assessment.first.strip())
        else:
            # log missing assesment
            pass

class Surf2SOERReport(object):
    """ Surf to SOER Report
    """
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
        """ Update from Surf
        """
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
                setattr(self, fname, [ value.strip().encode('utf8')
                                                        for value in field ])
            elif field.first is not None:
                setattr(self, fname, field.first.strip().encode('utf8'))
            else:
                setattr(self, fname, '')
        setattr(self, 'subject', context.subject)
        sortOrder = context.soer_sortOrder.first
        if sortOrder is not None:
            setattr(self, 'sortOrder', sortOrder.strip())
        self.topic = self.topic.decode('utf8')

    @property
    def portal_type(self):
        """ Portal type
        """
        portal_type = 'FlexibilityReport'
        topic = self.topic.lower()
        if topic == 'country introduction':
            portal_type = 'DiversityReport'
        elif topic in vocab.long_topics.keys():
            if self.question.decode('utf8') in \
                                      vocab.long_questions.values() + \
                                      vocab.old_long_questions.values():
                portal_type = 'CommonalityReport'
            elif self.question.decode('utf8') in \
                                 vocab.long_diversity_questions.values() + \
                                 vocab.old_long_diversity_questions.values():
                portal_type = 'DiversityReport'
        if portal_type != 'FlexibilityReport':
            self.topic = topic
        return portal_type

    def hasFigure(self):
        """ Has figure
        """
        context = self.context
        if context.soer_hasFigure:
            #i = 0
            for fig in context.soer_hasFigure:
                try:
                    fileName = fig.soer_fileName.first and \
                                    str(fig.soer_fileName.first) or 'tempfile'
                except Exception:
                    log.log('Figure resource without information %s' %
                                              fig, severity=log.logging.WARN)
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
                        fileName = dataSrc.soer_fileName.first and \
                                str(dataSrc.soer_fileName.first) or 'tempfile'
                        result['dataSource'] = {
                            'url' : dataSrc.subject.strip(),
                            'fileName' : fileName,
                            'dataURL' : dataSrc.soer_dataURL.first.strip() }
                    else:
                        result['dataSource'] = {
                            'url' : str(dataSrc),
                            'fileName' : fileName,
                            'dataURL' : str(dataSrc) }
                        log.log('Data source without information %s' %
                                           dataSrc, severity=log.logging.WARN)

                yield result

    def dataSource(self):
        """ Data source
        """
        context = self.context
        if context.soer_dataSource:
            for dataSrc in context.soer_dataSource:
                yield { 'url' : dataSrc.subject.strip(),
                        'fileName' : dataSrc.soer_fileName.first.strip(),
                        'dataURL' : dataSrc.soer_dataURL.first.strip() }

    def relatedIndicator(self):
        """ Related indicator
        """
        context = self.context
        if context.soer_relatedEuropeanIndicator:
            return [ str(indicator) for indicator in
                          context.soer_relatedEuropeanIndicator ]
        return []

class SoerRDF2Surf(object):
    """ Read a rdf and verify that the feed is correct before content is updated
        in Plone.
    """
    implements(ISoerRDF2Surf)

    def __init__(self, url):
        self.store = surf.Store(reader='rdflib',
                                writer='rdflib',
                                rdflib_store = 'IOMemory')
        self.store.log.setLevel(logging.CRITICAL)
        self.store.writer.log.setLevel(logging.CRITICAL)
        self.session = surf.Session(self.store, mapping={
                                  surf.ns.SOER.NationalStory: NationalStory})
        self.loadUrl(url)

    def loadUrl(self, url):
        """ Load Url
        """
        self.store.load_triples(source=url)

    def channel(self):
        """ Channel
        """
        channel = self.session.get_class(surf.ns.SOER['Channel']).all()
        if not channel:
            channel = self.session.get_class(surf.ns.SOER['channel']).all()
        if channel and channel.first():
            channel = channel.first()
            result = {'organisationName':
                          getSingleValue(channel.soer_organisationName),
                      'organisationURL':
                          getSingleValue(channel.soer_organisationURL),
                      'organisationContactURL':
                          getSingleValue(channel.soer_organisationContactURL),
                      'organisationLogoURL':
                          getSingleValue(channel.soer_organisationLogoURL),
                      'license': getSingleValue(channel.soer_license),
                      'updated': DateTime()}
            return result

    def nationalStories(self):
        """ National stories
        """
        natStory = self.session.get_class(surf.ns.SOER['NationalStory'])
        for nstory in natStory.all().order():
            yield ISOERReport(nstory)

    def nationalStory(self, subject):
        """ National story
        """
        natStory = self.session.get_class(surf.ns.SOER['NationalStory'])
        return self.session.get_resource(subject, natStory)

    nsFormating = "\n%s\n%20s %6s %9s %5s %7s %8s %8s %10s %6s %5s\n"
    figFormating = "%s\n%20s %6s %9s %5s %7s\n"
    def status(self):
        """ Status
        """
        result = ""
        natStory = self.session.get_class(surf.ns.SOER['NationalStory'])
        #DataFile = self.session.get_class(surf.ns.SOER['DataFile'])
        result += self.nsFormating % (' ', ' ', 'Topic', 'Question', 'Desc',
                                      'KeyMsg', 'Assesment', 'KeyWord',
                                      'Indicator', 'Figure', 'Data')
        for nstory in natStory.all().order():
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
        """ Check channel
        """
        pass

    def _checkNationalStory(self, nstory):
        """ Check national story
        """
        #subjectSize = len(nstory.subject)
        #if subjectSize > 20:
        #    subject = nstory.subject[subjectSize-20:]
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
        """ Check figure
        """
        #subjectSize = len(fig['url'])
        #if subjectSize > 20:
        #    subject = fig['url'][subjectSize-20:]
        result = self.figFormating % (fig['url'],
                                      'Figure',
                                    chk(fig['mediaType']),
                                    chk(fig['caption']),
                                    chk(fig['description']),
                                    chk(fig['dataSource'])
                                    )
        return result

    def _checkDataSource(self, dataSrc):
        """ Check data source
        """
        #subjectSize = len(dataSrc['url'])
        #if subjectSize > 20:
        #    subject = dataSrc['url'][subjectSize-20:]
        result = self.figFormating % (dataSrc['url'],
                                      'DataSource','','',
                                    chk(dataSrc['fileName']),
                                    chk(dataSrc['dataURL'])
                                    )
        return result

def chk(context):
    """ Check
    """
    return context and 'OK' or 'Miss'
