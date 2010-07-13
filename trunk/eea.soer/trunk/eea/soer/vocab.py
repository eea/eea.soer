from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
import surf

# Maps values from eea.soer.vocab.topics to their full description
long_topics = {
    u'air pollution': u"Air pollution - urban and rural air quality, national and transboundary pollution, measures",
    u'climate change': u"Climate change mitigation - GHG emissions trends and projections national measures",
    u'biodiversity': u"Nature protection and biodiversity - protected areas, 2010 target, measures",
    u'land': u"Land - CLC 1990-2006 - stocks, changes, drivers",
    u'freshwater': u"Freshwaters - surface and ground, quality and quantity, WFD, measures",
    u'waste': u"Waste - waste generation, treatment and prevention, measures",
}

# Maps values from eea.soer.vocab.questions to their full description
long_questions = {
    u'0': u"Why should we care?",
    u'1': u"What are the state and impacts?",
    u'2': u"What are the related drivers and pressures?",
    u'3': u"What is the 2020 outlook?",
    u'4': u"What are the policy responses?",
}

# Maps values from eea.soer.vocab.diversity_questions to their full description
long_diversity_questions = {
    u'10': u"What distinguishes the country?",
    u'11': u"What are the major societal trends?",
    u'12': u"What are the main drivers?",
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
        (u'3', "Outlook to 2020"),
        (u'4', "Policy responses"),
    ),

    'eea.soer.vocab.diversity_questions': (
        (u'10', 'Factors'),
        (u'11', 'Societal developments'),
        (u'12', 'Main drivers'),
        (u'13', 'Main developments'),
    ),

}

atvocabs['eea.soer.vocab.all_questions'] = atvocabs['eea.soer.vocab.diversity_questions'] + atvocabs['eea.soer.vocab.questions']

geostore = surf.Store(reader='rdflib',  writer='rdflib', rdflib_store = 'IOMemory')
geosession = surf.Session(geostore)
surf.ns.register(ROD="http://rod.eionet.europa.eu/schema.rdf#")
#geostore.load_triples(source="http://rod.eionet.europa.eu/countries")        
atvocabs['eea.soer.vocab.geo_coverage'] = []
Locality = geosession.get_class(surf.ns.ROD['Locality'])

surf.ns.register(NUTS="http://rdfdata.eionet.europa.eu/ramon/ontology/")

for loc in Locality.all().order():
    atvocabs['eea.soer.vocab.geo_coverage'].append((loc.rod_loccode.first.strip(), loc.rdfs_label.first.strip()))


# geostore.load_triples(source="http://rdfdata.eionet.europa.eu/ramon/send_all")
# use local file to speed up for now
from eea.soer.tests.base import nutsrdf
geostore.load_triples(source=nutsrdf)


class NUTSRegions(object):
    """ All regions """

    implements(IVocabularyFactory)

    def __call__(self, context=None):
        NUTSRegion = geosession.get_class(surf.ns.NUTS['NUTSRegion'])
        vocabulary = []
        for region in NUTSRegion.all().order():
            vocabulary.append(SimpleTerm(region.subject.strip(),
                                         token=region.nuts_code.first.strip(),
                                         title=region.nuts_name.first.strip()))
        return SimpleVocabulary(vocabulary)

    def resources(self):
        NUTSRegion = geosession.get_class(surf.ns.NUTS['NUTSRegion'])
        return NUTSRegion.all().order()
    
    def getCode(self, subject):
        NUTSRegion = geosession.get_class(surf.ns.NUTS['NUTSRegion'])
        region = NUTSRegion(subject).nuts_code.first
        if region:
            return region.strip()
        return ''
    
VocabularyFactory = NUTSRegions()
