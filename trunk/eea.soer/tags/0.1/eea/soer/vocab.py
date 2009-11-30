from Products.PloneLanguageTool.availablelanguages import countries as all_countries
from eea.vocab import countries

# Maps values from eea.soer.vocab.topics to their full description
long_topics = {
    '0': "Air pollution - urban and rural air quality, national and transboundary pollution, measures",
    '1': "Climate change mitigation - GHG emissions trends and projections national measures",
    '2': "Nature protection and biodiversity - protected areas, 2010 target, measures",
    '3': "Land - CLC 1990-2006 - stocks, changes, drivers",
    '4': "Freshwaters - surface and ground, quality and quantity, WFD, measures",
    '5': "Waste - waste generation, treatment and prevention, measures",
}

# Maps values from eea.soer.vocab.sections to their full description
long_sections = {
    '0': "Why should we care about this theme?",
    '1': "What are the state (S) and impacts (I) related to this theme, including impacts on the natural environment and human health/human well-being, both at national level as well as in transboundary terms?",
    '2': "Drivers and pressures, long""",
    '3': "What is the 2020 outlook (date flexible) for the topic in question and how will this affect possiband human health/well-being?", 
    '4': "Which responses (R) have been put in place or are planned at national level for the theme in question?",
}

# Maps values from eea.soer.vocab.diversity_questions to their full description
long_diversity_questions = {
    '0': 'What are the factors that distinguish your country from many others?',
    '1': 'What have been the major societal developments since 1980 compared with the period 1950-1980?',
    '2': 'What are the main drivers of environmental pressures and how do these contribute to multiple impacts on people and the natural environment?',
    '3': 'What are the foreseen main developments in coming decades that could be expected to contribute most to future environmental pressures?',
}

atvocabs = {
    'eea.soer.vocab.topics': (
        ('0', "Air pollution"),
        ('1', "Climate change mitigation"),
        ('2', "Nature protection and biodiversity"),
        ('3', "Land"),
        ('4', "Freshwaters"),
        ('5', "Waste"),
    ),

    'eea.soer.vocab.sections': (
        ('0', "Why care?"),
        ('1', "State and impacts"),
        ('2', "Drivers and pressures"),
        ('3', "Policy responses"),
        ('4', "Outlook to 2020"),
    ),

    'eea.soer.vocab.diversity_questions': (
        ('0', 'Factors'),
        ('1', 'Societal developments'),
        ('2', 'Main drivers'),
        ('3', 'Main developments'),
    ),

    'eea.soer.vocab.content_types': (
        ('0', "Text only"),
        ('1', "Figures only"),
        ('2', "Indicators and figures"),
    ),
}

atvocabs['eea.soer.vocab.european_countries'] = []
european_country_codes = countries.getCountries()
for i in european_country_codes:
    country_name = all_countries[i.upper()]
    atvocabs['eea.soer.vocab.european_countries'].append((i, country_name))
