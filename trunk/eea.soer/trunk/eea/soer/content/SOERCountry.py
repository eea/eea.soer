#import sys
from md5 import md5
#from StringIO import StringIO
#import traceback
from zope.interface import implements
#import surf
import urllib2 
from BeautifulSoup import BeautifulSoup
from AccessControl import ClassSecurityInfo
#from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.content.folder import ATFolder
from eea.soer.content.interfaces import IReportingCountry
from eea.soer.config import PROJECTNAME, ADD_CONTENT_PERMISSION
from eea.soer import vocab
from eea.soer import sense
from types import UnicodeType

try:
    from Products.LinguaPlone.public import registerType, Schema, StringField
    from Products.LinguaPlone.public import StringWidget
    registerType, Schema, StringField, StringWidget #pyflakes
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import registerType, Schema, StringField
    from Products.Archetypes.public import StringWidget

from Products.CMFPlone import log
import logging
logger = logging.getLogger('eea.soer.content.SOERCountry')

tidy = None
try:
    import tidy
except ImportError, err:
    logger.info(err)


schema = Schema((

    StringField(
        name='rdfFeed',
        languageIndependent=False,
        widget= StringWidget(
            size=70,
            label='RDF feed',
            label_msgid='label_feed_rdf_url',
            description='The address of the feed.',
            description_msgid='help_feed_rdf_url',
            i18n_domain='plone',
        ),
    ),

),
)

schema = getattr(ATFolder, 'schema', Schema(())).copy() + schema.copy()
schema['relatedItems'].widget.visible =  {'edit' : 'visible'}

def tidyUp(value):
    if tidy:
        if isinstance(value, UnicodeType):
            value = value.encode('utf8')

        parsed = tidy.parseString(
                        str(value), drop_empty_paras=1, indent_spaces=1, #indent="auto",
                        output_xhtml=1, word_2000=1, wrap=72, input_xml=0, tab_size=4,
                        show_body_only=True,
                        output_encoding='utf8',
                        input_encoding='utf8')
    else:
        return value

    return str(parsed)

class SOERCountry(ATFolder):
    """ """
    implements(IReportingCountry)

    security = ClassSecurityInfo()
    meta_type = 'SOERCountry'
    portal_type = 'SOERCountry'
    allowed_content_types = ['Image', 'CommonalityReport', 'DiversityReport',
                             'FlexibilityReport','DataSourceLink']
    _at_rename_after_creation = True

    schema = schema
    _v_feedUpdating = False
    feedHash = None

    def _isFeedChanged(self, feed):
        feedHash = md5(feed).hexdigest()
        log.log('%s, %s' % (feedHash, self.feedHash))
        if feedHash != self.feedHash:
            self.feedHash = feedHash
            return True
        return False

    security.declareProtected(ADD_CONTENT_PERMISSION, 'updateFromFeed')
    def updateFromFeed(self):
        """ update feed """
        url = self.getRdfFeed()
        if url:
            squidt = getToolByName(self, 'portal_squid', None)
            if squidt is not None:
                urlexpr = squidt.getUrlExpression()
                # use squid default url calculation during update due
                # acquisition problem to find the url expression script
                # XXX: maybe we should disable invalidation all together during update? 
                squidt.manage_setSquidSettings(squidt.getSquidURLs(), url_expression='')

            if self.aq_parent:
                self.aq_parent.manage_exportObject(id=self.getId())

            soer = sense.SoerRDF2Surf(url)
            for link in self.contentValues(filter={ 'portal_type' :'Link'}):
                url = link.getRemoteUrl()
                if url:
                    soer.loadUrl(url)
            self._updateFromFeed(soer)
            if squidt is not None:
                # restore the url expression 
                squidt.manage_setSquidSettings(squidt.getSquidURLs(), url_expression=urlexpr)
            
    def _updateFromFeed(self, soer): #pyflakes, #pylint: disable-msg = R0912, R0914, R0915
        language = self.Language() or 'en'
        self._v_feedUpdating = True
        reports = {}

        self.channel = channel = soer.channel()
        wtool = getToolByName(self, 'portal_workflow')

        def publishIfPossible(obj, action='publish'):
            actions = [a['id'] for a in wtool.getActionsFor(obj)]
            if action in actions:
                wtool.doActionFor(obj, action, comment='Automatic feed update')

        if channel and channel.get('organisationLogoURL', None):
            try:
                image = urllib2.urlopen(channel['organisationLogoURL'])
                image_data = image.read()
            except Exception:
                image_data = None
            if image_data:
                if not hasattr(self, 'logo'):
                    logo = self[self.invokeFactory('Image', id='logo',
                                                   image=image_data)]
                    publishIfPossible(logo)
                else:
                    logo = self['logo']
                    logo.setImage(image_data)

        def updateReport(nstory, report=None): #pyflakes, #pylint: disable-msg = R0912, R0914, R0915              
            parentReport = None
            if nstory.portal_type in ['DiversityReport', 'CommonalityReport']:
                questions = dict([[v, k] for k, v in vocab.old_long_diversity_questions.items()]) #pyflakes, #pylint: disable-msg = W0631
                questions.update(dict([[v, k] for k, v in vocab.long_questions.items()])) #pyflakes, #pylint: disable-msg = W0631
                # old labels before https://svn.eionet.europa.eu/projects/Zope/ticket/3685
                questions.update(dict([[v, k] for k, v in vocab.old_long_questions.items()]))            
                question = questions.get(nstory.question, nstory.question)
                #original_url = nstory.subject.strip()
            else:
                question = nstory.question
            if report is None:
                parentReport = reports.get((nstory.topic, nstory.question), None)
                if parentReport:
                    report = parentReport[parentReport.invokeFactory(nstory.portal_type, id='temp_report',
                                                                     topic=nstory.topic,
                                                                     question=question)]

                else:
                    report = self[self.invokeFactory(nstory.portal_type, id='temp_report',
                                                     topic=nstory.topic,
                                                     question=question)]
            report.setLanguage(language)
            report.setDescription(nstory.description)
            report.setKeyMessage(tidyUp(nstory.keyMessage))
            report.setGeoCoverage(nstory.geoCoverage)
            report.setSubject(nstory.keyword)
            report.setEvaluation(nstory.evaluation)
            newId = report._renameAfterCreation(check_auto_id=False)
            if parentReport is None:
                parentReport = report = self[newId]
                reports[(nstory.topic, nstory.question)] = report
            else:
                report = parentReport[newId]
                if hasattr(nstory,'sortOrder'):
                    parentReport.moveObjectToPosition(newId, int(nstory.sortOrder))
                else:
                    parentReport.moveObjectsToTop(ids=[newId])

            assessment = tidyUp(nstory.assessment)
            for fig in nstory.hasFigure():
                log.log('Fetching Figure: %s' % fig['url'])
                # read figure
                try:
                    image = urllib2.urlopen(fig['url'])
                except Exception:
                    log.log('FAILED: Fetching Figure: %s' % fig['url'])
                    continue
                image_data = image.read()
                if image_data:
                    figure = getattr(report, fig['fileName'], None)
                    if figure is not None:
                        continue
                    figure = report[report.invokeFactory('Image', id='tempfile',
                                                         image=image_data)]
                    figure.setTitle(fig['caption'] or fig['fileName'])
                    figure.setDescription(fig['description'])
                    newId = figure._renameAfterCreation(check_auto_id=False)
                    figure = report[newId]
                    publishIfPossible(figure)

                    if fig['url'] in assessment.decode('utf8'):
                        assessment = assessment.replace(fig['url'].encode('utf8'), 'resolveuid/%s' % figure.UID())
                    if fig.get('dataSource', None) is not None:
                        dataSrc = fig['dataSource']
                        dataLink = report[report.invokeFactory('DataSourceLink', id='tmpdatalink',
                                                               title=dataSrc['dataURL'],
                                                    remoteUrl=dataSrc['dataURL'])]
                        dataLink.setLanguage(language)
                        newId = dataLink._renameAfterCreation(check_auto_id=False)
                        dataLink = report[newId]                        
                        figure.setRelatedItems([dataLink])
                        publishIfPossible(dataLink)
                        
                    figure.setLanguage(language)
                    report.moveObjectToPosition(figure.getId(), fig['sortOrder'])
                    figure.reindexObject()
                else:
                    log.log('FAILED: Figure is empty: %s' % fig['url'])
            i = 0
            for indicatorUrl in nstory.relatedIndicator():
                i += 1
                if not indicatorUrl.startswith('http'):
                    # FIXME need to find out which indicator url it is for i.e CSI 018
                    continue
                title = u'Related indicator'
                try:
                    url = urllib2.urlopen(indicatorUrl)
                    soup = BeautifulSoup(url)
                    title = soup.title.string.encode('utf8').strip()
                except Exception: #pyflakes, #pylint: disable-msg = W0704
                    # we failed to get the title of the indicator, use 'Related Indicator'
                    pass

                indicator = report[report.invokeFactory('RelatedIndicatorLink', id='indicator%s' % i,
                                                             remoteUrl=indicatorUrl,
                                                             title=title)]

                publishIfPossible(indicator)

            report.setText(assessment, format='text/html')
            report.setEffectiveDate(nstory.pubDate)
            publishIfPossible(report)
            report.original_url = nstory.subject.strip()
            report.setModificationDate(nstory.modified)
            report.reindexObject()
            report.setModificationDate(nstory.modified)

        # find old reports, update them or remove them
        catalog = getToolByName(self, 'portal_catalog')
        toDeleteIds = [b.getId for b in catalog(path={'query' : '/'.join(self.getPhysicalPath()),
                               'depth' : 1},
                              portal_type=['CommonalityReport', 'DiversityReport','FlexibilityReport'])]
        if toDeleteIds:
            self.manage_delObjects(ids=toDeleteIds)
        # update the rest which should be all new reports
        for nstory in soer.nationalStories():
            updateReport(nstory)
            
        self._v_feedUpdating = False
        
def soerCountryUpdated(obj, event):
    if obj.getRdfFeed() and not obj._v_feedUpdating:
        obj.updateFromFeed()
        

registerType(SOERCountry, PROJECTNAME)
