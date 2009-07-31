========
eea.soer
========

The eea.soer package provides the SOERReport content type. You need to have
the AddPortalContent permission to add them:

  >>> self.setRoles(['Manager'])

SOERReports can be added to folders that provide the IPossibleSOERContainer
interface:

  >>> from eea.soer.interfaces import IPossibleSOERContainer
  >>> from zope.interface import alsoProvides

  >>> id = portal.invokeFactory('Folder', id='soer_reports')
  >>> reports = portal[id]
  >>> alsoProvides(reports, IPossibleSOERContainer)

  >>> id = reports.invokeFactory('SOERReport', id='testreport')
  >>> report = reports[id]
  >>> print report
  <SOERReport at testreport>

Let's fill in the add form:

  >>> form = {
  ...     'title': 'SV SOER Part C Report',
  ...     'description': 'SOER Part C Country Report From Sweden',
  ...     'text': 'The situation is serious :s',
  ...     'topics': "Air pollution – urban and rural air quality, national and transboundary pollution, measures",
  ...     'content_type': "Text only",
  ...     'sections': "Why care?",
  ...     'country': 'Sweden',
  ... }
  >>> report.processForm(values=form, data=1, metadata=1)

See if properties are applied:

  >>> report.Title()
  'SV SOER Part C Report'
  >>> report.Description()
  'SOER Part C Country Report From Sweden'
  >>> report.getText()
  '<p>The situation is serious :s</p>'
  >>> report.getContent_type()
  'Text only'
  >>> report.getSections()
  'Why care?'
  >>> report.getCountry()
  'Sweden'

