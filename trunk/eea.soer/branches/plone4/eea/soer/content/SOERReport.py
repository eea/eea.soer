""" SOER Report
"""
from zope.interface import implements, directlyProvides, alsoProvides
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.utils import DisplayList
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.newsitem import ATNewsItem
from eea.soer.content.interfaces import ISOERReport
from eea.soer.content.interfaces import ISoerFigure, ISoerDataFile
from Products.ATVocabularyManager import NamedVocabulary
from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
from Products.CMFPlone.PloneBatch import Batch
from Products.Archetypes.public import (
    Schema,
    TextField,
    AnnotationStorage,
    RichWidget,
    StringField,
    SelectionWidget
)

schema = Schema((
    TextField('keyMessage',
        required = False,
        searchable = True,
        primary = False,
        storage = AnnotationStorage(migrate=True),
        validators = ('isTidyHtmlWithCleanup',),
        default_content_type = zconf.ATNewsItem.default_content_type,
        default_output_type = 'text/x-html-safe',
        allowable_content_types = ('text/html',),
        widget = RichWidget(
            description = "Optional",
            description_msgid = "help_body_text",
            label = "Key message",
            label_msgid = "label_body_text",
            rows = 5,
            i18n_domain = "plone",
            allow_file_upload = False,
        ),
    ),

    TextField('text',
        required = True,
        searchable = True,
        primary = True,
        storage = AnnotationStorage(migrate=True),
        validators = ('isTidyHtmlWithCleanup',),
        default_content_type = zconf.ATNewsItem.default_content_type,
        default_output_type = 'text/x-html-safe',
        allowable_content_types = ('text/html',),
        widget = RichWidget(
            description = "",
            description_msgid = "help_body_text",
            label = "Assessment",
            label_msgid = "label_body_text",
            rows = 25,
            i18n_domain = "plone",
            allow_file_upload = zconf.ATDocument.allow_document_upload
        ),
    ),

    StringField(
        name='soerCountry',
        required = False,
        mode = 'r',
        widget=SelectionWidget(
            label='Country',
            label_msgid='eea.soer_label_country',
            i18n_domain='eea.soer',
            format='select',
        ),
        vocabulary=NamedVocabulary('eea.soer.vocab.european_countries'),
        enforceVocabulary=False,
    ),

    StringField(
        name='geoCoverage',
        required = True,
        widget=SelectionWidget(
            label='Geographical coverage',
            label_msgid='eea.soer_label_geocoverage',
            description='Required',
            i18n_domain='eea.soer',
            format='select',
        ),
        vocabulary="getGeoCoverageVocabulary",
        enforceVocabulary=False,
    ),

    StringField(
        name='topic',
        required = True,
        widget=SelectionWidget(
            label='Topics',
            label_msgid='eea.soer_label_topics',
            i18n_domain='eea.soer',
            format='select',
        ),
        vocabulary=NamedVocabulary('eea.soer.vocab.topics'),
        enforceVocabulary=True,
    ),

    StringField(
        name='question',
        required = True,
        widget=SelectionWidget(
            label='Question',
            label_msgid='eea.soer_label_questions',
            i18n_domain='eea.soer',
            format='select',
        ),
        vocabulary=NamedVocabulary('eea.soer.vocab.questions'),
        enforceVocabulary=True,
    ),

    StringField(
        name='evaluation',
        required=0,
        searchable=0,
        default=u'http://www.eea.europa.eu/soer/evaluations#XX',
        widget=SelectionWidget(
            label='Evaluation',
            label_msgid='label_evaluation',
            description='This is a two letter value which indicates quickly '
                        'what the evaluation and trend is.',
            visible={'view' : 'invisible',
                     'edit' : 'invisible'},
            format='select',
        ),
        vocabulary='getEvaluationVocabulary',
    ),
),
)

schema = getattr(ATFolder, 'schema', Schema(())).copy() + schema.copy()
schema['title'].default = 'not_set_yet'
schema['title'].required = 0
schema['title'].widget.visible = {'edit' : 'invisible'}
schema['description'].widget.description = \
                     '(Optional) ' + schema['description'].widget.description
schema['soerCountry'].default_method = 'default_country'
schema['relatedItems'].widget.visible =  {'edit' : 'visible'}
schema['relatedItems'].schemata = 'metadata'

class SOERReport(ATFolder, ATNewsItem):
    """ SOER Report
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(ATFolder, '__implements__', ()), )
    implements(ISOERReport)

    meta_type = 'SOERReport'
    portal_type = 'SOERReport'
    _at_rename_after_creation = True

    schema = schema
    content_icon = 'document_icon.gif'

    original_url = ''

    def getTermTitle(self, vocab_name, term_key):
        """ Utility method to get the title form a vocabulary term
        """
        portal = getToolByName(self, 'portal_url').getPortalObject()
        atvm = getToolByName(portal, ATVOCABULARYTOOL, None)
        vocab = atvm.getVocabularyByName(vocab_name)
        term = getattr(vocab, term_key, None)
        if term == None:
            return ''
        return term.title

    def getSoerCountryName(self):
        """ Get SOER country name
        """
        country_code = self.getSoerCountry()
        if len(country_code) > 2:
            # country folder id is probably named with full name
            return country_code
        return self.getTermTitle('eea.soer.vocab.european_countries',
                                 country_code)

    def getGeoCoverageVocabulary(self, content_instance=None, field=None):
        """ Get geo coverage vocabulary
        """
        vocab =  getUtility(IVocabularyFactory,
                            name=u"eea.soer.vocab.NUTSRegions")
        indent = u''
        parent = []
        displayList = DisplayList()

        displayList.add(u'', u'Select a region (required)')
        displayList.add(u'bio', u'-- Bio geo regions --')
        displayList.add(u'alpine', u'Alpine')
        displayList.add(u'carpathian', u'Carpathian')
        displayList.add(u'baltic', u'Baltic')
        displayList.add(u'countries', u'-- Countries --')
        for region in vocab.countries():
            current = region.subject.strip()
            displayList.add(current, region.nuts_name.first.strip())

        displayList.add(u'nuts', u'-- NUTS Regions --')
        for region in vocab.resources():
            current = region.subject.strip()
            if not current.startswith(
                          'http://rdfdata.eionet.europa.eu/ramon/nuts2008/'):
                continue

            if region.nuts_partOf.first:
                if region.nuts_partOf.first.subject.strip() not in parent:
                    indent += u'.'
                    parent.append(region.nuts_partOf.first.subject.strip())
                else:
                    while region.nuts_partOf.first.subject.strip() != \
                                                                  parent[-1]:
                        parent = parent[:-1]
                        indent = indent[:-1]

            elif len(parent) > 0:
                indent = u''
                parent = []
            title = u'%s %s' % (indent, region.nuts_name.first.strip())
            displayList.add(current, title)

        return displayList

    def getGeographicCoverage(self):
        """ Get geographic coverage
        """
        return self.getGeoCoverage()

    def getEvaluationVocabulary(self, content_instance=None, field=None):
        """ Get evaluation vocabulary
        """
        vocab = getUtility(IVocabularyFactory,
                           name=u"eea.soer.vocab.Evaluation")
        return DisplayList([(t.value, t.title) for t in vocab(self) ])

    def default_country(self):
        """ Default country
        """
        path = self.getPhysicalPath()
        if len(path) >= 2:
            if self.aq_parent.portal_type == self.portal_type:
                country_code = path[-3]
            else:
                country_code = path[-2]
            return country_code
        return ''

    def figures(self):
        """ Return figures for listing at the bottom of the report
        """
        assessment = self.getText()
        return Batch([fig for fig in
            self.getFolderContents(contentFilter={'portal_type': 'Image'})
            if fig.getURL(1) not in assessment ],
            10)

    def dataSources(self):
        """ Data sources
        """
        return self.getFolderContents(contentFilter= \
            {'portal_type': ['Link', 'DataSourceLink']}, full_objects=True)

    def indicators(self):
        """ Return indicators
        """
        return self.getFolderContents(contentFilter= \
                {'portal_type': 'RelatedIndicatorLink'}, full_objects=True)

    def subReports(self):
        """ Return reports inside this report (multiple indicator base report)
        """
        return self.getFolderContents(contentFilter= \
                      {'portal_type': self.portal_type}, full_objects=True)

    def isFromFeed(self):
        """ Return True if SOERCountry has a feed url
        """
        if hasattr(self.aq_parent, 'getRdfFeed'):
            return self.aq_parent.getRdfFeed() and True or False
        return False

    def absolute_url(self, **kwargs):
        """ Absolute url
        """
        return super(SOERReport, self).absolute_url(**kwargs)
        #parent = aq_inner(self).aq_parent
        #if parent.portal_type == self.portal_type:
            # we are subfolder lets fake url
        #    return '%s#%s' % (parent.absolute_url(*args), self.getId())

    def isSubReport(self):
        """ Is sub report
        """
        parent = aq_inner(self).aq_parent
        return parent.portal_type == self.portal_type

    def default_desc(self):
        """ Default desc
        """
        return ''

    def displayDescription(self):
        """ Display description
        """
        return self.Description() != self.default_desc()

def soerImageAdded(obj, event):
    """ SOER image added
    """
    if ISOERReport.providedBy(obj.aq_parent):
        alsoProvides(obj, ISoerFigure)

def soerLinkAdded(obj, event):
    """ SOER link added
    """
    if ISOERReport.providedBy(obj.aq_parent):
        directlyProvides(obj, ISoerDataFile)

def reportUpdated(obj, event):
    """ Report updated
    """
    keywords = list(obj.Subject())
    changed = False
    for keyword in ['SOER2010', 'country assessment', obj.getTopic()]:
        if keyword not in keywords:
            keywords.append(keyword)
            changed = True
    if changed:
        obj.setSubject(keywords)
