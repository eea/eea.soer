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

