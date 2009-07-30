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


User Interface
--------------

SOERReports are added through a web form:

  >>> from Products.Five.testbrowser import Browser
  >>> from Products.PloneTestCase.setup import portal_owner, default_password
  >>> browser = Browser()
  >>> browser.handleErrors = False

We must log in:

  >>> browser.open(self.portal.absolute_url())
  >>> browser.getControl(name='__ac_name').value = portal_owner
  >>> browser.getControl(name='__ac_password').value = default_password
  >>> browser.getControl(name='submit').click()

Now, when looking at the form, we can verify the existance and type of the
expected fields:

  >>> url = report.absolute_url() + '/edit'
  >>> browser.open(url)
  >>> form = browser.getForm('soerreport-base-edit')
  >>> for i in 'topics', 'content_type', 'sections', 'country':
  ...     ctl = form.getControl(name=i)
  ...     print ctl.type
  select
  select
  select
  select

