import sys
from md5 import md5
from StringIO import StringIO
import traceback
from zope.interface import implements
import surf
import urllib2 
from BeautifulSoup import BeautifulSoup
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.content.folder import ATFolder
from eea.soer.content.interfaces import IReportingCountry
from eea.soer.config import *
from eea.soer import vocab
from eea.soer import sense

try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import *
from Products.CMFPlone import log


schema = Schema((

    StringField(
        name='rdfFeed',
        languageIndependent=False,
        widget=StringWidget(
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
            toDeleteIds = []
            catalog = getToolByName(self, 'portal_catalog')
            for b in catalog(path='/'.join(self.getPhysicalPath()),
                         portal_type=['CommonalityReport', 'DiversityReport','FlexibilityReport']):
                if b.getId in self.objectIds() and b.getId not in toDeleteIds:
                    toDeleteIds.append(b.getId)
            log.log('Deleting %s' % toDeleteIds)
            self.manage_delObjects(ids=toDeleteIds)
        
            self._updateFromFeed(url)
            for link in self.contentValues(filter={ 'portal_type' :'Link'}):
                url = link.getRemoteUrl()
                if url:
                    log.log('Updating from extra feed %s' % url)
                    self._updateFromFeed(url)
            if squidt is not None:
                # restore the url expression 
                squidt.manage_setSquidSettings(squidt.getSquidURLs(), url_expression=urlexpr)
            
    def _updateFromFeed(self, url):
        log.log('Feed has changed, updating')
        language = self.Language() or 'en'
        self._v_feedUpdating = True
        reports = {}
        soer = sense.SoerRDF2Surf(url)
        self.channel = channel = soer.channel()
        wtool = getToolByName(self, 'portal_workflow')
        
        if channel and channel.get('organisationLogoURL',None):
            image = urllib2.urlopen(channel['organisationLogoURL'])
            image_data = image.read()
            if image_data:
                if not hasattr(self, 'logo'):
                    logo = self[self.invokeFactory('Image', id='logo',
                                                   image=image_data)]
                    if 'publish' in wtool.getActionsFor(logo):
                        wtool.doActionFor(logo, 'publish', comment='Automatic feed update')
                else:
                    logo = self['logo']
                    logo.setImage(image_data)


        parentReport = None
        for nstory in soer.nationalStories():
            questions = dict([[v,k] for k,v in vocab.long_diversity_questions.items()])
            questions.update(dict([[v,k] for k,v in vocab.long_questions.items()]))
            # old labels before https://svn.eionet.europa.eu/projects/Zope/ticket/3685
            questions.update(dict([[v,k] for k,v in vocab.old_long_questions.items()]))            
            question = questions.get(nstory.question, nstory.question)
            original_url = nstory.subject.strip()
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
            report.setKeyMessage(nstory.keyMessage)
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

            assessment = nstory.assessment
            for fig in nstory.hasFigure():
                log.log('Fetching Figure: %s' % fig['url'])
                # read figure
                try:
                    image = urllib2.urlopen(fig['url'])
                except:
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
                    if 'publish' in wtool.getActionsFor(figure):
                        wtool.doActionFor(figure, 'publish', comment='Automatic feed update')

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
                    figure.setLanguage(language)
                    report.moveObjectToPosition(figure.getId(), fig['sortOrder'])
                    figure.reindexObject()
                else:
                    log.log('FAILED: Figure is empty: %s' % fig['url'])
            i = 0
            for indicatorUrl in nstory.relatedIndicator():
                i += 1
                if not indicatorUrl.startswith('http'):
                    # FIXME need to find out which indicator url it si for i.e CSI 018
                    continue
                title = u'Related indicator'
                try:
                    url = urllib2.urlopen(indicatorUrl)
                    soup = BeautifulSoup(url)
                    title = soup.title.string.encode('utf8').strip()
                except:
                    # we failed to get the title of the indicator, use 'Related Indicator'
                    pass

                indicator = report[report.invokeFactory('RelatedIndicatorLink', id='indicator%s' % i,
                                                             remoteUrl=indicatorUrl,
                                                             title=title)]

                if 'publish' in wtool.getActionsFor(indicator):
                    wtool.doActionFor(indicator, 'publish', comment='Automatic feed update')

            report.setText(assessment, format='text/html')
            report.setEffectiveDate(nstory.pubDate)
            if 'publish' in wtool.getActionsFor(report):
                wtool.doActionFor(report, 'publish', comment='Automatic feed update')
            report.original_url = nstory.subject.strip()
            report.reindexObject()
        self._v_feedUpdating = False
        
def soerCountryUpdated(obj, event):
    if obj.getRdfFeed() and not obj._v_feedUpdating:
        obj.updateFromFeed()
        
    

registerType(SOERCountry, PROJECTNAME)
