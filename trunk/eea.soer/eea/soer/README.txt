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
  >>> print creport
  <CommonalityReport at commonality>


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
  'Global Warming - There is None'


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


Browser View
------------

Connected to the commonality report is a speicial browser view:

  >>> from elementtree import ElementTree as ET
  >>> creport.restrictedTraverse('commonality_report_view')
  <FSPageTemplate at /plone/commonality_report_view used for /plone/SOER/se/air-pollution-why-care>


Diversity Reports
-----------------

In the above examples we only looked at the CommonalityReport content type,
however there's also DiversityReport and FlexibilityReport. They are very
similar and work the same way:

  >>> id = reports.invokeFactory('DiversityReport', id='diversity')
  >>> dreport = reports[id]
  >>> print dreport
  <DiversityReport at diversity>

The diversity report have a few sections specified in a vocabulary that has to
be answered:

  >>> form = {
  ...     'soerSection': 'Some diverse question I have to answer',
  ...     'soerContentType': "Text only",
  ...     'soerCountry': 'Sweden',
  ...     'text': 'The situation is diverse!',
  ... }
  >>> dreport.processForm(values=form, data=1, metadata=1)
  >>> dreport.Title()
  'Diversity Report from Sweden'
  >>> dreport.Description()
  'SOER Part C Diversity Report from Sweden'
  >>> dreport.getSoerCountry()
  'Sweden'
  >>> dreport.getText()
  '<p>The situation is diverse!</p>'
  >>> dreport.getSoerSection()
  'Some diverse question I have to answer'


Flexibility Reports
-------------------

  >>> id = reports.invokeFactory('FlexibilityReport', id='flexibility')
  >>> freport = reports[id]
  >>> print freport
  <FlexibilityReport at flexibility>

Let's fill in the add form:

  >>> form = {
  ...     'soerContentType': "Text only",
  ...     'soerCountry': 'Sweden',
  ...     'text': 'The situation is flexible!',
  ... }
  >>> freport.processForm(values=form, data=1, metadata=1)
  >>> freport.Title()
  'Flexibility Report from Sweden'
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
  >>> creport.reindexObject()
  >>> dreport.reindexObject()
  >>> freport.reindexObject()

  >>> query = {'portal_type': 'CommonalityReport'}
  >>> catalog.searchResults(query)[0].getObject()
  <CommonalityReport at /plone/SOER/se/air-pollution-why-care>

  >>> query = {'getSoerSection': 'Why care?'}
  >>> catalog.searchResults(query)[0].getObject()
  <CommonalityReport at /plone/SOER/se/air-pollution-why-care>

  >>> query = {'getSoerTopic': 'Air Pollution'}
  >>> catalog.searchResults(query)[0].getObject()
  <CommonalityReport at /plone/SOER/se/air-pollution-why-care>

  >>> query = {'getSoerContentType': 'Text only'}
  >>> for i in catalog.searchResults(query):
  ...     print i.getObject()
  <CommonalityReport at air-pollution-why-care>
  <DiversityReport at diversity-report-from-sweden>
  <FlexibilityReport at flexibility-report-from-sweden>

  >>> query = {'getSoerCountry': 'Sweden'}
  >>> for i in catalog.searchResults(query):
  ...     print i.getObject()
  <CommonalityReport at air-pollution-why-care>
  <DiversityReport at diversity-report-from-sweden>
  <FlexibilityReport at flexibility-report-from-sweden>

