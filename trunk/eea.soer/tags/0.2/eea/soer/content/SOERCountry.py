from zope.interface import implements
import surf
import urllib
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
            soer = sense.SoerRDF2Surf(url)
            wtool = getToolByName(self, 'portal_workflow')
            self.manage_delObjects(ids=self.objectIds())
            parentReport = None
            for nstory in soer.nationalStories():
                questions = dict([[v,k] for k,v in vocab.long_diversity_questions.items()])
                questions.update(dict([[v,k] for k,v in vocab.long_questions.items()]))

                
                if parentReport and parentReport.original_url in nstory.subject.strip():
                    if nstory.portal_type == 'DiversityReport':
                        import pdb; pdb.set_trace()
                    report = parentReport[parentReport.invokeFactory(nstory.portal_type, id='temp_report',
                                                 topic=nstory.topic,
                                                 question=questions.get(nstory.question, ''))]
                    
                else:
                    report = self[self.invokeFactory(nstory.portal_type, id='temp_report',
                                                 topic=nstory.topic,
                                                 question=questions.get(nstory.question, ''))]
                    parentReport = None
                report.setText(nstory.assessment)

                report.setDescription(nstory.description)
                report.setKeyMessage(nstory.keyMessage)
                report.setGeoCoverage(nstory.geoCoverage)
                newId = report._renameAfterCreation(check_auto_id=False)
                if parentReport is None:
                    parentReport = report = self[newId]
                else:
                    report = parentReport[newId]

                for fig in nstory.hasFigure():
                    # read figure
                    try:
                        image = urllib.urlopen(fig['url'])
                    except:
                        continue
                    image_data = image.read()
                    if image_data:
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
                        if fig.get('dataSource', None) is not None:
                            dataSrc = fig['dataSource']
                            dataLink = report[report.invokeFactory('Link', id=dataSrc['fileName'],
                                                        remoteUrl=dataSrc['dataURL'])]
                            figure.setRelatedItems([dataLink])
                        figure.reindexObject()

                        
                report.setEffectiveDate(nstory.pubDate)
                try:
                    wtool.doActionFor(report, 'publish', comment='Automatic feed update')
                except:
                    log('Failed to publish %s' % figure.absolute_url())                
                report.original_url = nstory.subject.strip()
                report.reindexObject()

def updateFromFeed(obj, event):
    pass
    
registerType(SOERCountry, PROJECTNAME)
