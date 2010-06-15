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
from Products.CMFPlone.log import log


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
                             'FlexibilityReport','Link']
    _at_rename_after_creation = True

    schema = schema

    security.declareProtected(ADD_CONTENT_PERMISSION, 'updateFromFeed')
    def updateFromFeed(self):
        """ update feed """
        url = self.getRdfFeed()
        if url:
            reports = {}
            soer = sense.SoerRDF2Surf(url)
            self.channel = channel = soer.channel()
            if channel and channel.get('organisationLogoURL',None):
                image = urllib2.urlopen(channel['organisationLogoURL'])
                image_data = image.read()
                if image_data:
                    if not hasattr(self, 'logo'):
                        logo = self[self.invokeFactory('Image', id='logo',
                                                       image=image_data)]
                        try: 
                            wtool.doActionFor(logo, 'publish', comment='Automatic feed update')
                        except:
                            log('Failed to publish %s' % logo.absolute_url())
                    else:
                        logo = self['logo']
                        logo.setImage(image_data)
                    
                    
            wtool = getToolByName(self, 'portal_workflow')
            oldContentIds = [ oId for oId, obj in self.objectItems()
                              if obj.portal_type not in ['Image','RSSFeedRecipe']]
            log('Deleting %s' % oldContentIds)
            self.manage_delObjects(ids=oldContentIds)
            parentReport = None
            for nstory in soer.nationalStories():
                questions = dict([[v,k] for k,v in vocab.long_diversity_questions.items()])
                questions.update(dict([[v,k] for k,v in vocab.long_questions.items()]))
                question = questions.get(nstory.question, '')
                parentReport = reports.get((nstory.topic, nstory.question), None)
                if parentReport:
                    report = parentReport[parentReport.invokeFactory(nstory.portal_type, id='temp_report',
                                                                     topic=nstory.topic,
                                                                     question=question)]
                    
                else:
                    report = self[self.invokeFactory(nstory.portal_type, id='temp_report',
                                                 topic=nstory.topic,
                                                 question=questions.get(nstory.question, ''))]

                report.setDescription(nstory.description)
                report.setKeyMessage(nstory.keyMessage)
                report.setGeoCoverage(nstory.geoCoverage)
                report.setSubject(nstory.keyword)
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
                    log('Fetching Figure: %s' % fig['url'])
                    # read figure
                    try:
                        image = urllib2.urlopen(fig['url'])
                    except:
                        continue
                    image_data = image.read()
                    if image_data:
                        figure = getattr(report, fig['fileName'], None)
                        if figure is not None:
                            continue
                        figure = report[report.invokeFactory('Image', id=fig['fileName'],
                                                             image=image_data)]
                        figure.setTitle(fig['caption'])
                        figure.setDescription(fig['description'])
                        if fig['fileName'] == 'tempfile':
                            newId = figure._renameAfterCreation(check_auto_id=False)
                            figure = report[newId]
                        try:
                            wtool.doActionFor(figure, 'publish', comment='Automatic feed update')
                        except:
                            log('Failed to publish %s' % figure.absolute_url())

                        if fig['url'] in assessment.decode('utf8'):
                            assessment = assessment.replace(fig['url'], 'resolveuid/%s' % figure.UID())
                        if fig.get('dataSource', None) is not None:
                            dataSrc = fig['dataSource']
                            dataLink = report[report.invokeFactory('Link', id=dataSrc['fileName'],
                                                                   title=dataSrc['fileName'],
                                                        remoteUrl=dataSrc['dataURL'])]
                            figure.setRelatedItems([dataLink])
                        figure.reindexObject()
                i = 0
                for indicatorUrl in nstory.relatedIndicator():
                    i += 1
                    if not indicatorUrl.startswith('http'):
                        # FIXME need to find out which indicator url it si for i.e CSI 018
                        continue
                    soup = BeautifulSoup(urllib2.urlopen(indicatorUrl))
                    
                    indicator = report[report.invokeFactory('RelatedIndicatorLink', id='indicator%s' % i,
                                                            remoteUrl=indicatorUrl,
                                                            title=soup.title.string.encode('utf8'))]

                    try:
                        wtool.doActionFor(indicator, 'publish', comment='Automatic feed update')
                    except:
                        log('Failed to publish %s' % indicator.absolute_url())                
                    
                report.setText(assessment, format='text/html')
                report.setEffectiveDate(nstory.pubDate)
                try:
                    wtool.doActionFor(report, 'publish', comment='Automatic feed update')
                except:
                    log('Failed to publish %s' % report.absolute_url())                
                report.original_url = nstory.subject.strip()
                report.reindexObject()

def updateFromFeed(obj, event):
    pass
    
registerType(SOERCountry, PROJECTNAME)
