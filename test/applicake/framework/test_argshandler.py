'''
Created on Apr 22, 2012

@author: quandtan
'''
import unittest
import sys
#from applicake.framework.argshandler import ApplicationArgsHandler
#from applicake.framework.argshandler import BasicArgsHandler
#from applicake.framework.argshandler import WrapperArgsHandler
from applicake.framework.argshandler import *
from applicake.framework.logger import Logger
from StringIO import StringIO


class Test(unittest.TestCase):
    def setUp(self):
        self.log_stream = StringIO()
        self.log = Logger.create(level='DEBUG', name='memory_logger', stream=self.log_stream)

    def tearDown(self):
        pass

    def test_ArgsHandler(self):
        ''' '''
        handler = ArgsHandler()
        handler.add_runner_args('-i', '--INPUT', required=False, dest="INPUT", action='store',
                                help="Input (configuration) file")
        handler.add_runner_args('-o', '--OUTPUT', required=False, dest="OUTPUT", action='store',
                                help="Output (configuration) file")
        sys.argv = ['--INPUT', 'in1.ini', '--OUTPUT', 'out.ini']
        pargs, defaultargs = handler.get_parsed_arguments(self.log, sys.argv)
        expected = {'INPUT': 'in1.ini',
                    'OUTPUT': 'out.ini'}
        self.assertDictEqual(pargs, expected)

        handler.add_app_args(self.log, 'TEMPLATE', 'test template')
        sys.argv.extend(['--TEMPLATE', 'my.tpl'])
        pargs, defaultargs = handler.get_parsed_arguments(self.log, sys.argv)
        expected['TEMPLATE'] = 'my.tpl'
        self.assertDictEqual(pargs, expected)

        try:
            sys.argv = sys.argv[:-2]
            sys.argv.extend(['--TEMPLATE', 'my.tpl'])
            self.assertTrue(False, 'Method call should fail')
        except:
            assert True

        try:
            sys.argv = sys.argv[:-2]
            sys.argv.extend(['--TEMPLATE', 'my.tpl'])
            assert True
        except:
            self.assertTrue(False, 'Method call should NOT fail')
        self.assertTrue(handler.get_app_argnames() == ['TEMPLATE'], handler.get_app_argnames())

    def test_ArgsHandler_bug1(self):
        ''' '''
        handler = ArgsHandler()
        handler.add_app_args(self.log, 'GETCODES', 'getcodes', action='store_true', default=False)

        pargs, defaultargs = handler.get_parsed_arguments(self.log, ['--GETCODES'])
        expected = {'GETCODES': True}
        self.assertDictEqual(pargs, expected)

        pargs, defaultargs = handler.get_parsed_arguments(self.log, [])
        expected = {'GETCODES': False}

        self.assertDictEqual(defaultargs, expected)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
