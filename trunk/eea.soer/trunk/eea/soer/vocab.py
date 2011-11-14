""" Vocab
"""
from zope.schema.interfaces import IVocabularyFactory
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from Products.CMFCore.utils import getToolByName
import surf

# Maps values from eea.soer.vocab.topics to their full description
long_topics = {
    u'air pollution': (u"Air pollution - urban and rural air quality, "
                       "national and transboundary pollution, measures"),
    u'climate change': (u"Climate change mitigation - GHG emissions trends "
                        "and projections national measures"),
    u'biodiversity': (u"Nature protection and biodiversity - protected "
                       "areas, 2010 target, measures"),
    u'land': u"Land - CLC 1990-2006 - stocks, changes, drivers",
    u'freshwater': (u"Freshwaters - surface and ground, quality and "
                     "quantity, WFD, measures"),
    u'waste': u"Waste - waste generation, treatment and prevention, measures",
}

# Maps values from eea.soer.vocab.questions to their full description
old_long_questions = {
    u'0': u"Why should we care?",
    u'1': u"What are the state and impacts?",
    u'2': u"What are the related drivers and pressures?",
    u'3': u"What is the 2020 outlook?",
    u'4': u"What are the policy responses?",
}

old_long_diversity_questions = {
    u'10': u"What distinguishes the country?",
    u'11': u"What are the major societal trends?",
    u'12': u"What are the main drivers?",
    u'13': u"What are the foreseen developments?",
}

# Maps values from eea.soer.vocab.questions to their full description
long_questions = {
    u'0': u"Why should we care about this issue",
    u'1': u"The state and impacts",
    u'2': u"The key drivers and pressures",
    u'3': u"The 2020 outlook",
    u'4': u"Existing and planned responses",
}

# Maps values from eea.soer.vocab.diversity_questions to their full description
long_diversity_questions = {
    u'10': u"What distinguishes the country?",
    u'11': u"What have been the major societal developments?",
    u'12': u"What are the main drivers of environmental pressures?",
    u'13': u"What are the foreseen developments?",
}

atvocabs = {
    'eea.soer.vocab.topics': (
        (u'air pollution', "Air pollution"),
        (u'climate change', "Climate change mitigation"),
        (u'biodiversity', "Nature protection and biodiversity"),
        (u'land', "Land use"),
        (u'freshwater', "Freshwater"),
        (u'waste', "Waste"),
    ),

    'eea.soer.vocab.questions': (
        (u'0', "Why care?"),
        (u'1', "State and impacts"),
        (u'2', "Drivers and pressures"),
        (u'3', "Outlook 2020"),
        (u'4', "National responses"),
    ),

    'eea.soer.vocab.diversity_questions': (
        (u'10', 'Distinguishing factors'),
        (u'11', 'Societal developments'),
        (u'12', 'Drivers and impacts'),
        (u'13', 'Future developments'),
    ),

}

atvocabs['eea.soer.vocab.all_questions'] = \
                           atvocabs['eea.soer.vocab.diversity_questions'] + \
                           atvocabs['eea.soer.vocab.questions']

geostore = surf.Store(reader='rdflib',
                      writer='rdflib',
                      rdflib_store = 'IOMemory')
geosession = surf.Session(geostore)
surf.ns.register(ROD="http://rod.eionet.europa.eu/schema.rdf#")
#geostore.load_triples(source="http://rod.eionet.europa.eu/countries")
atvocabs['eea.soer.vocab.geo_coverage'] = []
Locality = geosession.get_class(surf.ns.ROD['Locality'])

surf.ns.register(NUTS="http://rdfdata.eionet.europa.eu/ramon/ontology/")
surf.ns.register(EVALUATION= \
                        "http://www.eea.europa.eu/soer/rdfs/evaluation/1.0#")

for loc in Locality.all().order():
    atvocabs['eea.soer.vocab.geo_coverage'].append(
               (loc.rod_loccode.first.strip(), loc.rdfs_label.first.strip()))

#geostore.load_triples(source="http://rdfdata.eionet.europa.eu/ramon/send_all")
# use local file to speed up for now
from eea.soer.config import nutsrdf, evalrdf, spatialrdf
geostore.load_triples(source=nutsrdf)
geostore.load_triples(source=evalrdf)
geostore.load_triples(source=spatialrdf)

class NUTSRegions(object):
    """ All regions
    """
    implements(IVocabularyFactory)

    @property
    def rdfClass(self):
        """ RDF class
        """
        return geosession.get_class(surf.ns.NUTS['NUTSRegion'])

    @property
    def namespace(self):
        """ Namespace
        """
        return u'nuts'

    def __call__(self, context=None):
        RdfClass = self.rdfClass
        vocabulary = []
        prefix = self.namespace + u'_%s'
        for i in RdfClass.all().order():
            url = i.subject.strip()
            # we only want NUTS2008 list to have unique entires
            nuts_2008 = 'http://rdfdata.eionet.europa.eu/ramon/nuts2008/'
            if url.startswith(nuts_2008):
                vocabulary.append(SimpleTerm(
  url,
  token=u'nutscode2008_%s' % getattr(i, prefix % 'code').first.strip(),
  title=getattr(i, prefix % 'name').first.strip()))
            if url.startswith('http://rdfdata.eionet.europa.eu/ramon/nuts/'):
                vocabulary.append(SimpleTerm(
  url,
  token=u'nutscode_%s' % getattr(i, prefix % 'code').first.strip(),
  title=getattr(i, prefix % 'name').first.strip()))
        for i in self.countries():
            url = i.subject.strip()
            vocabulary.append(SimpleTerm(
  url,
  token=u'countrycode_%s' % getattr(i, prefix % 'code').first.strip(),
  title=getattr(i, prefix % 'name').first.strip()))
        return SimpleVocabulary(vocabulary)

    def resources(self):
        """ Resources
        """
        return self.rdfClass.all().order()

    def countries(self):
        """ Countries
        """
        return geosession.get_class(surf.ns.NUTS['CountryCode']).all().order()

    def getCode(self, subject):
        """ Get code
        """
        for rdfClass in [surf.ns.NUTS['CountryCode'],
                         surf.ns.NUTS['NUTSRegion'],
                         surf.ns.ROD['Spatial']]:
            region = geosession.get_resource(subject, rdfClass)
            if region is not None and region.nuts_code.first is not None:
                return region.nuts_code.first.strip()
            if region is not None and region.rod_spatialTwoletter.first is \
                                                                     not None:
                return region.rod_spatialTwoletter.first.strip()
        return u''

NUTSVocabularyFactory = NUTSRegions()

regions = {'alpine' : u'Alpine',
           'carpathian' : u'Carpathian',
           'baltic' : u'Baltic' }

class UsedGeoCoverage(object):
    """ Only used regions
    """
    implements(IVocabularyFactory)

    def __call__(self, context=None):
        cat = getToolByName(context, 'portal_catalog')
        uniqueValues = []
        try:
            uniqueValues = cat.uniqueValuesFor('getGeographicCoverage')
        except KeyError:
            try:
                uniqueValues = cat.uniqueValuesFor('getGeoCoverage')
            except KeyError:
                return SimpleVocabulary([])
        NutsRegion = geosession.get_class(surf.ns.NUTS['NUTSRegion'])
        CountryCode = geosession.get_class(surf.ns.NUTS['CountryCode'])
        result = []
        for geo in uniqueValues:
            res = None
            rdf_eionet = 'http://rdfdata.eionet.europa.eu/ramon/'
            if geo.startswith(rdf_eionet + 'nuts2008/'):
                res = geosession.get_resource(geo, NutsRegion)
                token = u'nuts2008_%s' % res.nuts_code.first.strip()
                title = res.nuts_name.first.strip()
            elif  geo.startswith(rdf_eionet + 'nuts/'):
                res = geosession.get_resource(geo, NutsRegion)
                token = u'nuts_%s' % res.nuts_code.first.strip()
                title = res.nuts_name.first.strip()
            elif geo.startswith(rdf_eionet + 'countries/'):
                res = geosession.get_resource(geo, CountryCode)
                token = u'country_%s' % res.nuts_code.first.strip()
                title = res.nuts_name.first.strip()
            elif geo.startswith('http://rod.eionet.europa.eu/spatial/'):
                res = geosession.get_resource(geo, Locality)
                token = u'rod_%s' % res.rod_spatialTwoletter.first.strip(),
                title = res.rod_spatialName.first.strip()
            elif geo in regions.keys():
                token = u'region_%s' % geo
                title = regions.get(geo)
                res = True
            if res:
                result.append(SimpleTerm(geo,
                                         token=token,
                                         title=title))
        def attrgetter(obj):
            """ Attr getter
            """
            return obj.title
        result = sorted(result, key=attrgetter)

        return SimpleVocabulary(result)

UsedGeoCoverageFactory = UsedGeoCoverage()

class Evaluations(object):
    """ Evaluations vocabulary
    """
    implements(IVocabularyFactory)

    @property
    def rdfClass(self):
        """ RDF class
        """
        return geosession.get_class(surf.ns.EVALUATION['Evaluation'])

    @property
    def namespace(self):
        """ Namespace
        """
        return u'evaluation'

    def __call__(self, context=None):
        RdfClass = self.rdfClass
        vocabulary = []
        prefix = self.namespace + u'_%s'
        for i in RdfClass.all().order():
            url = i.subject.strip()
            vocabulary.append(
                        SimpleTerm(
                             url,
                             token=getattr(i, prefix % 'code').first.strip(),
                             title=getattr(i, prefix % 'name').first.strip()))
        return SimpleVocabulary(vocabulary)

    def getCode(self, subject):
        """ Get code
        """
        Evaluation = self.rdfClass
        evaluation = Evaluation(subject).evaluation_code.first
        if evaluation:
            return evaluation.strip()
        return u''

EvalVocabularyFactory = Evaluations()

class PortalTypesVocabulary(object):
    """ Vocabulary factory for soer portal types.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        ttool = getToolByName(context, 'portal_types', None)
        if ttool is None:
            return None
        items = [ SimpleTerm(t, t, ttool[t].Title())
                  for t in ['CommonalityReport',
                            'DiversityReport',
                            'FlexibilityReport']]
        return SimpleVocabulary(items)

PortalTypesVocabularyFactory = PortalTypesVocabulary()
