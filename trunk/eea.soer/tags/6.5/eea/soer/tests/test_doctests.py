""" Doctests
"""
import doctest
import unittest
from eea.soer.tests.base import SOERFunctionalTestCase
from Testing.ZopeTestCase import FunctionalDocFileSuite

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def test_suite():
    """ Test suite
    """
    return unittest.TestSuite((
            FunctionalDocFileSuite('README.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.soer',
                  test_class=SOERFunctionalTestCase),
            FunctionalDocFileSuite('catalog.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.soer',
                  test_class=SOERFunctionalTestCase),
            FunctionalDocFileSuite('sense.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.soer',
                  test_class=SOERFunctionalTestCase),
            FunctionalDocFileSuite('report.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.soer.browser',
                  test_class=SOERFunctionalTestCase),
            ))
