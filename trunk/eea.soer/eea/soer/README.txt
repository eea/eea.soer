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

Let's fill in the add form:

  >>> form = {
  ...     'title': 'Swedish environment report',
  ...     'text': 'The situation is serious :s',
  ...     'topics': "Air pollution – urban and rural air quality, national and transboundary pollution, measures",
  ...     'content_type': "Text only",
  ...     'sections': "Why care?",
  ...     'country': 'Sweden',
  ... }
  >>> report.processForm(values=form, data=1, metadata=1)

When description is not provided, it's generated using the language code from
the parent folder.

  >>> report.Description()
  'SOER Part C Report from Sweden'

Verify the properties of the other fields:

  >>> report.getText()
  '<p>The situation is serious :s</p>'
  >>> report.getContent_type()
  'Text only'
  >>> report.getSections()
  'Why care?'
  >>> report.getCountry()
  'Sweden'

