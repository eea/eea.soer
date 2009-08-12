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


Form Processing
---------------

Let's fill in the add form:

  >>> form = {
  ...     'title': 'Swedish environment report',
  ...     'text': 'The situation is serious :s',
  ...     'soerTopic': "Blablabla",
  ...     'soerContentType': "Text only",
  ...     'soerSection': "Why care?",
  ...     'soerCountry': 'Sweden',
  ... }
  >>> report.processForm(values=form, data=1, metadata=1)

Verify the properties of the other fields:

  >>> report.getText()
  '<p>The situation is serious :s</p>'
  >>> report.getSoerContentType()
  'Text only'
  >>> report.getSoerSection()
  'Why care?'
  >>> report.getSoerTopic()
  'Blablabla'
  >>> report.getSoerCountry()
  'Sweden'


SOERReport View
---------------

Connected to SOERReports is a special view, creatively named soerreport_view:

  >>> from elementtree import ElementTree as ET
  >>> report.restrictedTraverse('soerreport_view')
  <FSPageTemplate at /plone/soerreport_view used for /plone/SOER/se/swedish-environment-report>


Catalog
-------

To make it possible to use eea.facetednavigation on SOERReports, we have added
catalog indexes for topic, section, content type and country:

  >>> from Products.CMFCore.utils import getToolByName
  >>> catalog = getToolByName(self.portal, 'portal_catalog')
  >>> report.reindexObject()

  >>> query = {'portal_type': 'SOERReport'}
  >>> catalog.searchResults(query)[0].getObject()
  <SOERReport at /plone/SOER/se/swedish-environment-report>

  >>> query = {'getSoerSection': 'Why care?'}
  >>> catalog.searchResults(query)[0].getObject()
  <SOERReport at /plone/SOER/se/swedish-environment-report>

  >>> query = {'getSoerTopic': 'Blablabla'}
  >>> catalog.searchResults(query)[0].getObject()
  <SOERReport at /plone/SOER/se/swedish-environment-report>

  >>> query = {'getSoerContentType': 'Text only'}
  >>> catalog.searchResults(query)[0].getObject()
  <SOERReport at /plone/SOER/se/swedish-environment-report>

  >>> query = {'getSoerCountry': 'Sweden'}
  >>> catalog.searchResults(query)[0].getObject()
  <SOERReport at /plone/SOER/se/swedish-environment-report>

