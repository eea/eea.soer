from Products.PloneLanguageTool.availablelanguages import countries as all_countries
from eea.vocab import countries


topics = [
   "Air pollution – urban and rural air quality, national and transboundary pollution, measures",
   "Climate change mitigation – GHG emissions trends and projections national measures",
   "Nature protection and biodiversity – protected areas, 2010 target, measures",
   "Land – CLC 1990-2006 - stocks, changes, drivers",
   "Freshwaters – surface and ground, quality and quantity, WFD, measures",
   "Waste – waste generation, treatment and prevention, measures",
]

content_types = [
   "Text only",
   "Figures only",
   "Indicators and figure",
   "News feed",
]

sections = [
   "Why care?",
   "State and impacts",
   "Drivers and pressures",
   "Policy responses",
   "Outlook to 2020",
]

european_country_codes = countries.getCountries()
european_countries = {}
for i in european_country_codes:
    european_countries[i] = all_countries[i.upper()]
