from zope.interface import implements
import surf
import urllib
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.content.folder import ATFolder
from eea.soer.content.interfaces import ISOERReportingCountry
from eea.soer.config import *
from eea.soer import vocab

try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import *


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
    implements(ISOERReportingCountry)

    security = ClassSecurityInfo()
    meta_type = 'SOERCountry'
    portal_type = 'SOERCountry'
    allowed_content_types = ['Image', 'CommonalityReport', 'DiversityReport', 'FlexibilityReport','Link']
    _at_rename_after_creation = True

    schema = schema

    security.declareProtected(ADD_CONTENT_PERMISSION, 'update')
    def updateFeed(self):
        """ update feed """
        url = self.getRdfFeed()
        if url:
            wtool = getToolByName(self, 'portal_workflow')
            self.manage_delObjects(ids=self.objectIds())
            store = surf.Store(reader='rdflib',  writer='rdflib', rdflib_store = 'IOMemory')
            session = surf.Session(store)
            surf.ns.register(SOER="http://www.eea.europa.eu/soer/1.0#")
            store.load_triples(source=url)        
            
            NationalStory = session.get_class(surf.ns.SOER['NationalStory'])
            for nstory in NationalStory.all():
                topic = nstory.soer_topic.first.strip()
                question = nstory.soer_question.first.strip()
                questions = dict([[v,k] for k,v in vocab.long_diversity_questions.items()])
                questions.update(dict([[v,k] for k,v in vocab.long_questions.items()]))
                if topic == u'country introduction':
                    portal_type = 'DiversityReport'                                            
                elif topic in [u'air pollution', u'freshwater', u'climate change',
                               u'land', u'waste', u'biodiversity']:
                    if question in vocab.long_questions.values():
                        portal_type = 'CommonalityReport'
                    elif question in vocab.long_diversity_questions.values():
                        portal_type = 'DiversityReport'                        
                else:
                    portal_type = 'FlexibilityReport'                                            
                report = self[self.invokeFactory(portal_type, id='temp_report',
                                                 soerTopic=topic,
                                                 soerQuestion=questions[question])]

                if nstory.soer_assessment.first is not None:
                    report.setText(nstory.soer_assessment.first.strip())
                else:
                    # log missing assesment
                    pass

                
                report.setDescription(nstory.soer_keyMessage.first.strip())
                report.setGeoCoverage(nstory.soer_geoCoverage.first.strip())
                report._renameAfterCreation(check_auto_id=False)

                if nstory.soer_hasFigure:
                    for fig in nstory.soer_hasFigure:
                        # read figure
                        image = urllib.urlopen(fig.subject.strip())
                        image_data = image.read()
                        if image_data:
                            figure = report[report.invokeFactory('Image', id=fig.soer_fileName.first.strip(),
                                            image=image_data)]
                            wtool.doActionFor(figure, 'publish', comment='Automatic feed update')
                        for dataFile in fig.soer_dataSource:
                            dataFileObj = report[report.invokeFactory('Link', id=dataFile.soer_fileName.first.strip(),
                                                                       remoteUrl=dataFile.soer_dataURL.first.strip())]
                            figure.setRelatedItems(figure.getRelatedItems().append(dataFileObj))
                            wtool.doActionFor(dataFileObj, 'publish', comment='Automatic feed update')

                report.setEffectiveDate(nstory.soer_pubDate.first.strip())
                wtool.doActionFor(report, 'publish', comment='Automatic feed update')
                report.original_url = nstory.subject.strip()
                report.reindexObject()
                
registerType(SOERCountry, PROJECTNAME)
