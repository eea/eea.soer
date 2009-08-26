========
eea.soer
========

The eea.soer package provides the SOER report content types. You need to have
the AddPortalContent permission to add them.


Commonality Reports
-------------------

We'll start by looking at the Commonality Report. It's designed to answer
questions divided into topics with sections:

  >>> self.setRoles(['Manager'])
  >>> reports = self.portal.SOER.se
  >>> id = reports.invokeFactory('CommonalityReport', id='commonality')
  >>> creport = reports[id]


Default Values
--------------

When description is not provided, it's generated using the language code from
the parent folder.

  >>> creport.getSoerCountry()
  'Sweden'
  >>> creport.Description()
  'SOER Part C Commonality Report from Sweden'

The title is generated from the topic and section combination. It's changed
after saving/modifiying the report. Notice how only the first portion of
the topic is being used:

  >>> creport.setSoerTopic("Global Warming - Ice Cream's Worst Nightmare?")
  >>> creport.setSoerSection('There is None')
  >>> from zope.event import notify
  >>> from zope.app.event.objectevent import ObjectModifiedEvent
  >>> notify(ObjectModifiedEvent(creport))
  >>> creport.Title()
  'Global Warming - There is None (Sweden)'


Form Processing
---------------

Let's fill in the add form:

  >>> form = {
  ...     'text': 'The situation is serious :s',
  ...     'soerTopic': "Air Pollution",
  ...     'soerSection': "Why care?",
  ...     'soerContentType': "Text only",
  ...     'soerCountry': 'Sweden',
  ... }
  >>> creport.processForm(values=form, data=1, metadata=1)

Verify the properties of the other fields:

  >>> creport.getText()
  '<p>The situation is serious :s</p>'
  >>> creport.getSoerContentType()
  'Text only'
  >>> creport.getSoerSection()
  'Why care?'
  >>> creport.getSoerTopic()
  'Air Pollution'
  >>> creport.getSoerCountry()
  'Sweden'

The countries typically adds a lot of CommonalityReports, one for each
topic/section combination. Let's test adding one more, answering another
question:

  >>> id = reports.invokeFactory('CommonalityReport', id='creport2')
  >>> creport2 = reports[id]
  >>> form = {
  ...     'text': 'The situation is serious :s',
  ...     'soerTopic': "Climate change mitigation - GHG emissions trends and projections national measures",
  ...     'soerSection': "Why care?",
  ...     'soerContentType': "Text only",
  ...     'soerCountry': 'Sweden',
  ... }
  >>> creport2.processForm(values=form, data=1, metadata=1)

The generated titles doesn't clash with the other commonality reports:

  >>> creport.Title()
  'Air Pollution - Why care? (Sweden)'
  >>> creport2.Title()
  'Climate change mitigation - Why care? (Sweden)'


Browser View
------------

Connected to the commonality report is a speicial browser view:

  >>> from elementtree import ElementTree as ET
  >>> creport.restrictedTraverse('commonality_report_view')
  <FSPageTemplate at ...>


Diversity Reports
-----------------

In the above examples we only looked at the CommonalityReport content type,
however there's also DiversityReport and FlexibilityReport. They are very
similar and work the same way:

  >>> id = reports.invokeFactory('DiversityReport', id='diversity')
  >>> dreport = reports[id]

The diversity report have a few sections specified in a vocabulary that has to
be answered:

  >>> form = {
  ...     'soerSection': 'What are the factors that distinguish your country from many others?',
  ...     'soerContentType': "Text only",
  ...     'soerCountry': 'Sweden',
  ...     'text': 'The situation is diverse!',
  ... }
  >>> dreport.processForm(values=form, data=1, metadata=1)
  >>> dreport.Title()
  'Diversity Report: What are the factors that distinguish your country from many others? (Sweden)'
  >>> dreport.Description()
  'SOER Part C Diversity Report from Sweden'
  >>> dreport.getSoerCountry()
  'Sweden'
  >>> dreport.getText()
  '<p>The situation is diverse!</p>'
  >>> dreport.getSoerSection()
  'What are the factors that distinguish your country from many others?'

Just like CommonalityReports, DiversityReports are designed to be created
multiple times by each country, answering one question per content object.
Therefore, it's important that titles don't clash:

  >>> id = reports.invokeFactory('DiversityReport', id='dreport2')
  >>> dreport2 = reports[id]
  >>> form = {
  ...     'text': 'The situation is serious :s',
  ...     'soerSection': 'What have been the major societal developments since 1980 compared with the period 1950-1980?',
  ...     'soerContentType': "Text only",
  ...     'soerCountry': 'Sweden',
  ... }
  >>> dreport2.processForm(values=form, data=1, metadata=1)

  >>> dreport.Title()
  'Diversity Report: What are the factors that distinguish your country from many others? (Sweden)'
  >>> dreport2.Title()
  'Diversity Report: What have been the major societal developments since 1980 compared with the period 1950 (Sweden)'


Flexibility Reports
-------------------

Flexibility reports are the simplest kind. They're just composed of one big
text area with free text. Only one should ever need to be created, therefore
the titles only need to be unique to the country:

  >>> id = reports.invokeFactory('FlexibilityReport', id='flexibility')
  >>> freport = reports[id]

Let's fill in the add form:

  >>> form = {
  ...     'soerContentType': "Text only",
  ...     'soerCountry': 'Sweden',
  ...     'text': 'The situation is flexible!',
  ... }
  >>> freport.processForm(values=form, data=1, metadata=1)
  >>> freport.Title()
  'Flexibility Report (Sweden)'
  >>> freport.Description()
  'SOER Part C Flexibility Report from Sweden'
  >>> freport.getSoerCountry()
  'Sweden'
  >>> freport.getText()
  '<p>The situation is flexible!</p>'


Catalog
-------

To make it possible to use eea.facetednavigation on SOER reports, we have added
catalog indexes for topic, section, content type and country:

  >>> from Products.CMFCore.utils import getToolByName
  >>> catalog = getToolByName(self.portal, 'portal_catalog')

We now have a couple of SOERReports indexed:

  >>> query = {
  ...     'portal_type': [
  ...         'CommonalityReport',
  ...         'DiversityReport',
  ...         'FlexibilityReport',
  ...      ]
  ... }
  >>> for i in catalog(query):
  ...     print i.getObject()
  <CommonalityReport at air-pollution-why-care-sweden>
  <CommonalityReport at climate-change-mitigation-why-care-sweden>
  <DiversityReport at diversity-report-what-are-the-factors-that-distinguish-your-country-from-many-others-sweden>
  <DiversityReport at diversity-report-what-have-been-the-major-societal-developments-since-1980-compared-with-the-period-1950-sweden>
  <FlexibilityReport at flexibility-report-sweden>

The DiversityReport and CommonalityReport share the same attribute/index to
indicate which question is being answered:

  >>> query = {'getSoerSection': 'Why care?'}
  >>> catalog(query)[0].getObject()
  <CommonalityReport at /plone/SOER/se/air-pollution-why-care-sweden>
  >>> query = {'getSoerSection': 'What are the factors that distinguish your country from many others?'}
  >>> catalog(query)[0].getObject()
  <DiversityReport at /plone/SOER/se/diversity-report-what-are-the-factors-that-distinguish-your-country-from-many-others-sweden>


The soerTopic attribute is only for CommonalityReports:

  >>> query = {'getSoerTopic': 'Air Pollution'}
  >>> catalog(query)[0].getObject()
  <CommonalityReport at /plone/SOER/se/air-pollution-why-care-sweden>

All SOERReports have the soerContentType attribute:

  >>> query = {'getSoerContentType': 'Text only'}
  >>> for i in catalog(query):
  ...     print i.getObject()
  <CommonalityReport at air-pollution-why-care-sweden>
  <CommonalityReport at climate-change-mitigation-why-care-sweden>
  <DiversityReport at diversity-report-what-are-the-factors-that-distinguish-your-country-from-many-others-sweden>
  <DiversityReport at diversity-report-what-have-been-the-major-societal-developments-since-1980-compared-with-the-period-1950-sweden>
  <FlexibilityReport at flexibility-report-sweden>

... and the soerCountry attribute:

  >>> query = {'getSoerCountry': 'Sweden'}
  >>> for i in catalog(query):
  ...     print i.getObject()
  <CommonalityReport at air-pollution-why-care-sweden>
  <CommonalityReport at climate-change-mitigation-why-care-sweden>
  <DiversityReport at diversity-report-what-are-the-factors-that-distinguish-your-country-from-many-others-sweden>
  <DiversityReport at diversity-report-what-have-been-the-major-societal-developments-since-1980-compared-with-the-period-1950-sweden>
  <FlexibilityReport at flexibility-report-sweden>

