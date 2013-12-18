from plone.i18n.locales.interfaces import ICountryAvailability

from zope.component import queryUtility
from eea.vocab import countries
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
        (u'land', "Land"),
        (u'freshwater', "Freshwaters"),
        (u'waste', "Waste"),
    ),

    'eea.soer.vocab.questions': (
        ('0', "Why care?"),
        ('1', "State and impacts"),
        ('2', "Drivers and pressures"),
        ('3', "Policy responses"),
        ('4', "Outlook to 2020"),
    ),

    'eea.soer.vocab.diversity_questions': (
        ('10', 'Factors'),
        ('11', 'Societal developments'),
        ('12', 'Main drivers'),
        ('13', 'Main developments'),
    ),


    'eea.soer.vocab.content_types': (
        ('0', "Text only"),
        ('1', "Figures only"),
        ('2', "Indicators and figures"),
    ),
    'eea.soer.vocab.geographical_coverage': (
        ('0', "AA"),
        ('1', "AB"),
        ('2', "AC"),
    ),

}

atvocabs['eea.soer.vocab.all_questions'] = atvocabs['eea.soer.vocab.diversity_questions'] + atvocabs['eea.soer.vocab.questions']




geostore = surf.Store(reader='rdflib',  writer='rdflib', rdflib_store = 'IOMemory')
geosession = surf.Session(geostore)
surf.ns.register(ROD="http://rod.eionet.europa.eu/schema.rdf#")
geostore.load_triples(source="http://rod.eionet.europa.eu/countries")        
atvocabs['eea.soer.vocab.geo_coverage'] = []
Locality = geosession.get_class(surf.ns.ROD['Locality'])

for loc in Locality.all():
    atvocabs['eea.soer.vocab.geo_coverage'].append((loc.rod_loccode.first.strip(), loc.rdfs_label.first.strip()))