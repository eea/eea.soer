========
eea.soer
========

The eea.soer package provides the SOER report content types. There are
currently three kind of reports:

Commonality Reports
-------------------

We'll start by looking at the Commonality Report. It's designed to answer
questions divided into topics with sections:

  >>> self.setRoles(['Manager'])
  >>> soer = self.portal.SOER
  >>> reports = soer[soer.invokeFactory('SOERCountry', id='se')]
  >>> id = reports.invokeFactory('CommonalityReport', id='commonality')
  >>> report = reports[id]

When description is not provided, it's generated using the language code from
the parent folder.

  >>> report.Description()
  'SOER Common environmental theme from Sweden'

The title is generated from the topic and section combination. It's changed
after saving/modifiying the report.

  >>> form = {
  ...     'text': 'The situation is serious :s',
  ...     'topic': u'climate change',
  ...     'question': u'2',
  ... }
  >>> report.processForm(values=form, data=1, metadata=1)

Verify the properties of the other fields:

  >>> report.Title()
  'Climate change mitigation - Drivers and pressures (Sweden)'
  >>> report.getText()
  '<p>The situation is serious :s</p>'


Diversity Reports
-----------------

In the above examples we only looked at the CommonalityReport content type,
however there's also DiversityReport and FlexibilityReport. They are very
similar and work the same way:

  >>> id = reports.invokeFactory('DiversityReport', id='diversity')
  >>> report = reports[id]

The diversity report have a few sections specified in a vocabulary that has to
be answered:

  >>> form = {
  ...     'question': u'10',
  ...     'text': u'The situation is diverse!',
  ...     'topic': u'any topic',
  ... }
  >>> report.processForm(values=form, data=1, metadata=1)
  >>> report.Title()
  'Country profile - Distinguishing factors (Sweden)'
  >>> report.Description()
  'SOER Country profile from Sweden'
  >>> report.getText()
  '<p>The situation is diverse!</p>'


Flexibility Reports
-------------------

Flexibility reports are the simplest kind. They're just composed of one big
text area with free text. Only one should ever need to be created, therefore
the titles only need to be unique to the country:

  >>> id = reports.invokeFactory('FlexibilityReport', id='flexibility')
  >>> report = reports[id]

Let's fill in the add form:

  >>> form = {
  ...     'text': 'The situation is flexible!',
  ...     'question': 'My own question?',
  ... }
  >>> report.processForm(values=form, data=1, metadata=1)
  >>> report.Title()
  'National and regional story (Sweden) - My own question?'
  >>> report.Description()
  'SOER National and regional story from Sweden'
  >>> report.getText()
  '<p>The situation is flexible!</p>'


--------------------------
SENSE feeds update process
--------------------------

See https://svn.eionet.europa.eu/projects/Zope/wiki/SENSEfeedUpdate
