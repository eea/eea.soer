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

            for nstory in soer.nationalStories():
                questions = dict([[v,k] for k,v in vocab.long_diversity_questions.items()])
                questions.update(dict([[v,k] for k,v in vocab.long_questions.items()]))
                
                report = self[self.invokeFactory(nstory.portal_type, id='temp_report',
                                                 topic=nstory.topic,
                                                 question=questions.get(nstory.question, ''))]

                report.setText(nstory.assessment)

                report.setDescription(nstory.description)
                report.setKeyMessage(nstory.keyMessage)
                report.setGeoCoverage(nstory.geoCoverage)
                newId = report._renameAfterCreation(check_auto_id=False)
                report = self[newId]
                for fig in nstory.hasFigure():
                    # read figure
                    image = urllib.urlopen(fig['url'])
                    image_data = image.read()
                    if image_data:
                        figure = report[report.invokeFactory('Image', id=fig['fileName'],
                                                             image=image_data)]
                        figure.setTitle(fig['caption'])
                        figure.setDescription(fig['description'])
                        wtool.doActionFor(figure, 'publish', comment='Automatic feed update')
                        figure.reindexObject()

                #report.setEffectiveDate(nstory.pubDate)
                wtool.doActionFor(report, 'publish', comment='Automatic feed update')
                #report.original_url = nstory.subject.strip()
                report.reindexObject()
                
registerType(SOERCountry, PROJECTNAME)
