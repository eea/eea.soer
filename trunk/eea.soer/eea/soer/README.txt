========
eea.soer
========

The eea.soer package provides the SOERReport content type. You need to have
the AddPortalContent permission to add them:

  >>> self.setRoles(['Manager'])
  >>> reports = self.portal.SOER.se
  >>> id = reports.invokeFactory('SOERReport', id='testreport')
  >>> report = reports[id]
  >>> print report
  <SOERReport at testreport>


Default Values
--------------

When description is not provided, it's generated using the language code from
the parent folder.

  >>> report.getSoerCountry()
  'Sweden'
  >>> report.Description()
  'SOER Part C Report from Sweden'

The title is generated from the topic and section combination. It's changed
after saving/modifiying the report:

  >>> report.setSoerTopic('Global Warming')
  >>> report.setSoerSection('There is None')
  >>> from zope.event import notify
  >>> from zope.app.event.objectevent import ObjectModifiedEvent
  >>> notify(ObjectModifiedEvent(report))
  >>> report.Title()
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
  >>> report.processForm(values=form, data=1, metadata=1)

Verify the properties of the other fields=

  >>> report.getText()
  '<p>The situation is serious :s</p>'
  >>> report.getSoerContentType()
  'Text only'
  >>> report.getSoerSection()
  'Why care?'
  >>> report.getSoerTopic()
  'Air Pollution'
  >>> report.getSoerCountry()
  'Sweden'


SOERReport View
---------------

Connected to SOERReports is a special view, creatively named soerreport_view:

  >>> from elementtree import ElementTree as ET
  >>> report.restrictedTraverse('soerreport_view')
  <FSPageTemplate at /plone/soerreport_view used for /plone/SOER/se/air-pollution-why-care>


Catalog
-------

To make it possible to use eea.facetednavigation on SOERReports, we have added
catalog indexes for topic, section, content type and country:

  >>> from Products.CMFCore.utils import getToolByName
  >>> catalog = getToolByName(self.portal, 'portal_catalog')
  >>> report.reindexObject()

  >>> query = {'portal_type': 'SOERReport'}
  >>> catalog.searchResults(query)[0].getObject()
  <SOERReport at /plone/SOER/se/air-pollution-why-care>

  >>> query = {'getSoerSection': 'Why care?'}
  >>> catalog.searchResults(query)[0].getObject()
  <SOERReport at /plone/SOER/se/air-pollution-why-care>

  >>> query = {'getSoerTopic': 'Air Pollution'}
  >>> catalog.searchResults(query)[0].getObject()
  <SOERReport at /plone/SOER/se/air-pollution-why-care>

  >>> query = {'getSoerContentType': 'Text only'}
  >>> catalog.searchResults(query)[0].getObject()
  <SOERReport at /plone/SOER/se/air-pollution-why-care>

  >>> query = {'getSoerCountry': 'Sweden'}
  >>> catalog.searchResults(query)[0].getObject()
  <SOERReport at /plone/SOER/se/air-pollution-why-care>

