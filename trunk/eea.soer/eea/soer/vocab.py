from Products.PloneLanguageTool.availablelanguages import countries as all_countries
from eea.vocab import countries


topics = [
    "Air pollution - urban and rural air quality, national and transboundary pollution, measures",
    "Climate change mitigation - GHG emissions trends and projections national measures",
    "Nature protection and biodiversity - protected areas, 2010 target, measures",
    "Land - CLC 1990-2006 - stocks, changes, drivers",
    "Freshwaters – surface and ground, quality and quantity, WFD, measures",
    "Waste - waste generation, treatment and prevention, measures",
]

sections = [
    "Why care?",
    "State and impacts",
    "Drivers and pressures",
    "Policy responses",
    "Outlook to 2020",
]

long_sections = {
    "Why care?":
        """Why should we care about this theme?""",

    "State and impacts":
        """What are the state (S) and impacts (I) related to this theme, 
        including impacts on the natural environment and human 
        health/human well-being, both at national level as well as in 
        transboundary terms?""",

    "Drivers and pressures":
        """Drivers and pressures, long""",

    "Policy responses":
        """
        What is the 2020 outlook (date flexible) for the topic in question 
        and how will this affect possiband human health/well-being? 
        """,

    "Outlook to 2020":
        """
        Which responses (R) have been put in place or are planned at 
        national level for the theme in question? 
        """,
}

content_types = [
    "Text only",
    "Figures only",
    "Indicators and figures",
]

diversity_questions = [
    'What are the factors that distinguish your country from many others?',
    'What have been the major societal developments since 1980 compared with the period 1950-1980?',
    'What are the main drivers of environmental pressures and how do these contribute to multiple impacts on people and the natural environment?',
    'What are the foreseen main developments in coming decades that could be expected to contribute most to future environmental pressures?',
]


european_country_codes = countries.getCountries()
european_countries = {}
for i in european_country_codes:
    european_countries[i] = all_countries[i.upper()]
