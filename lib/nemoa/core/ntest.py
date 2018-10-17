# -*- coding: utf-8 -*-
"""Testcases including setup and teardown for nemoa."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import unittest

from unittest import TestCase, TestResult, TestLoader, TestSuite, TextTestRunner
from io import StringIO

from nemoa.core import nmodule, nobject
from nemoa.types import Function, Method, OptStr

# Module variables
skip_compleness_test: bool = False

class GenericTestCase(TestCase):
    """Custom testcase."""

class ModuleTestCase(GenericTestCase):
    """Custom testcase."""

    module: str
    test_completeness: bool = True

    @unittest.skipIf(skip_compleness_test, "Completeness is not tested")
    def test_compleness_of_module(self) -> None:
        message: OptStr = None
        if hasattr(self, 'module') and self.test_completeness:
            mref = nmodule.inst(self.module)
            if hasattr(mref, '__all__'):
                required = set(getattr(mref, '__all__'))
            else:
                required = set()
                fdict = nobject.members(mref, base=Function)
                for attr in fdict.values():
                    name = attr['name']
                    if not name.startswith('_'):
                        required.add(name)
            tdict = nobject.members(self, base=Method, pattern='test_*')
            implemented = set()
            for attr in tdict.values():
                implemented.add(attr['name'][5:])
            complete = required <= implemented
            message = f"untested functions: '{required - implemented}'"
        else:
            complete = True
        self.assertTrue(complete, message)

    # def tearDown(self):
    #     """"""
    #     pass

def run_tests(
        stream: StringIO = StringIO(), verbosity: int = 2) -> TestResult:
    """Search and run testcases."""
    loader = TestLoader()
    suite = TestSuite()
    root = nmodule.root()
    cases = nmodule.search(root, base=GenericTestCase, val='reference')
    for ref in cases.values():
        suite.addTests(loader.loadTestsFromTestCase(ref))

    # Initialize runner and run testsuite
    return TextTestRunner(stream=stream, verbosity=verbosity).run(suite)
