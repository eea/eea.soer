""" EEA Soer installer
"""
from setuptools import setup, find_packages
import os

NAME = 'eea.soer'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(os.path.join(*PATH)).read().strip()

setup(name=NAME,
      version=VERSION,
      description="EEA Soer",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='SENSE soer eea stateoftheenvironment rdf linkeddata',
      author='European Environment Agency',
      author_email='webadmin@eea.europa.eu',
      url="https://svn.eionet.europa.eu/projects/"
          "Zope/browser/trunk/eea.soer",
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['eea'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'lxml',
          'surf',
          'rdflib',
          'BeautifulSoup',
          'eea.vocab',
          'eea.rdfmarshaller',
          'eea.facetednavigation',
          'eea.faceted.inheritance',
          'Products.ATVocabularyManager',
          'Products.LinguaPlone',
          'p4a.subtyper',
          'eea.themecentre',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
