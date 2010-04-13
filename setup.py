from setuptools import setup, find_packages
import os
from os.path import join

name = 'eea.soer'
path = name.split('.') + ['version.txt']
version = open(join(*path)).read().strip()

setup(name='eea.soer',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='',
      author_email='',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['eea'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'uuid',
          'surf',
          'surf.rdflib',
          'eea.vocab',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
