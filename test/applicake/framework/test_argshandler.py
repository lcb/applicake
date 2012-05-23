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
        self.log = Logger.create(level='DEBUG',name='memory_logger',stream=self.log_stream)

    def tearDown(self):
        pass 
        
    def test_ArgsHandler(self):
        ''' '''
        handler = ArgsHandler()         
        sys.argv = ['test.py','-i','in1.ini','-o','out.ini',
                    '-n','my name','-s','file','-l','DEBUG']      
        pargs = handler.get_parsed_arguments(self.log)
        expected = {'INPUTS': ['in1.ini'], 
                    'LOG_LEVEL': 'DEBUG', 
                    'NAME': 'my name', 
                    'STORAGE': 'file', 
                    'OUTPUT': 'out.ini'}
        self.assertDictEqual(pargs, expected)
        handler.add_app_args(self.log, 'template', 'test template')
        sys.argv.extend(['--TEMPLATE','my.tpl'])
        pargs = handler.get_parsed_arguments(self.log)
        expected['TEMPLATE'] = 'my.tpl'
        self.assertDictEqual(pargs, expected)
        try:
            sys.argv = sys.argv[:-2]
            sys.argv.extend(['--template','my.tpl'])            
            pargs = handler.get_parsed_arguments(self.log)
            self.assertTrue(False, 'Method call should fail')
        except:
            assert True
        try:
            sys.argv = sys.argv[:-2]
            sys.argv.extend(['--TEMPLATE','my.tpl'])          
            pargs = handler.get_parsed_arguments(self.log)
            assert True          
        except:
            self.assertTrue(False, 'Method call should NOT fail')
        self.assertTrue(handler.get_app_argnames() == ['TEMPLATE'], handler.get_app_argnames())
                      
            

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()