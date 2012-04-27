'''
Created on Apr 22, 2012

@author: quandtan
'''
import unittest
import sys
from applicake.framework.argshandler import ApplicationArgsHandler
from applicake.framework.argshandler import BasicArgsHandler
from applicake.framework.argshandler import WrapperArgsHandler
from applicake.framework.logger import Logger
from StringIO import StringIO

class Test(unittest.TestCase):


    def setUp(self):
        self.log_stream = StringIO()
        self.log = Logger.create(level='DEBUG',name='memory_logger',stream=self.log_stream)

    def tearDown(self):
        pass

    def test_basic_args_handler_1(self):
        '''Test if all defined aruments are optional'''
        handler = BasicArgsHandler()
        sys.argv = ['test.py'] # default if no cmd args are passed
        pargs = handler.get_parsed_arguments(self.log)
        expected = {}
        # needed to print the diff 
        self.maxDiff = None
        self.assertDictEqual(pargs, expected)
        
    def test_basic_args_handler_2(self):
        '''Test defined arguments'''
        handler = BasicArgsHandler()
        sys.argv = ['test.py','-i','in1.ini','-i','in2.ini','-o','out1.ini','-o','out2.ini',
                    '-g','gen1.ini','-g','gen2.ini','-c','col1.ini','-c','col2.ini']        
        pargs = handler.get_parsed_arguments(self.log)
        expected = {
                  'INPUTS':['in1.ini','in2.ini'],
                  'OUTPUT':'out2.ini', # 1st value of -o is overwritten
                  'GENERATORS':['gen1.ini','gen2.ini'],
                  'COLLECTORS':['col1.ini','col2.ini']                  
                  }
        # needed to print the diff 
        self.maxDiff = None
        self.assertDictEqual(pargs, expected)        


    def test_basic_args_handler_3(self):
        '''Test defined arguments and undefined arguments'''
        handler = BasicArgsHandler()
        sys.argv = ['test.py','-i','in1.ini','-i','in2.ini','-o','out1.ini','-o','out2.ini',
                    '-g','gen1.ini','-g','gen2.ini','-c','col1.ini','-c','col2.ini',
                    '--STORAGE','file','--BASEDIR','/tmp','--BASEDIR','/tmp/tmp']        
        pargs = handler.get_parsed_arguments(self.log)
        expected = {
                  'INPUTS':['in1.ini','in2.ini'],
                  'OUTPUT':'out2.ini', # 1st value of -o is overwritten
                  'GENERATORS':['gen1.ini','gen2.ini'],
                  'COLLECTORS':['col1.ini','col2.ini'],
                  'STORAGE': 'file',
                  'BASEDIR': '/tmp/tmp' # 1st value of --BASEDIR is overwritten                 
                  }
        # needed to print the diff 
        self.maxDiff = None
        self.assertDictEqual(pargs, expected)        

    def test_basic_args_handler_4(self):
        '''Test odd number of keys to values and if log contains ERROR entry'''
        handler = BasicArgsHandler()
        sys.argv = ['test.py','-i','in1.ini','-i','in2.ini','-o','out1.ini','-o','out2.ini',
                    '-g','gen1.ini','-g','gen2.ini','-c','col1.ini','-c','col2.ini',
                    '--STORAGE','file','--BASEDIR']        
        pargs = handler.get_parsed_arguments(self.log)
        expected = {
                  'INPUTS':['in1.ini','in2.ini'],
                  'OUTPUT':'out2.ini', # 1st value of -o is overwritten
                  'GENERATORS':['gen1.ini','gen2.ini'],
                  'COLLECTORS':['col1.ini','col2.ini'],               
                  }
        # needed to print the diff 
        self.maxDiff = None
        self.assertDictEqual(pargs, expected)
        self.log_stream.seek(0)
        log_content = self.log_stream.read()
        assert 'ERROR' in log_content        

    def test_basic_args_handler_5(self):
        '''Test wrong definition of a undefined key'''
        handler = BasicArgsHandler()
        sys.argv = ['test.py','-i','in1.ini','-i','in2.ini','-o','out1.ini','-o','out2.ini',
                    '-g','gen1.ini','-g','gen2.ini','-c','col1.ini','-c','col2.ini',
                    '--STORAGE','file','-BASEDIR','/tmp']        
        pargs = handler.get_parsed_arguments(self.log)
        expected = {
                  'INPUTS':['in1.ini','in2.ini'],
                  'OUTPUT':'out2.ini', # 1st value of -o is overwritten
                  'GENERATORS':['gen1.ini','gen2.ini'],
                  'COLLECTORS':['col1.ini','col2.ini'],
                  'STORAGE': 'file',                
                  }
        # needed to print the diff 
        self.maxDiff = None
        self.assertDictEqual(pargs, expected) 

    def test_application_args_handler_1(self):
        '''Test defined arguments'''
        handler = ApplicationArgsHandler()
        sys.argv = ['test.py','-i','in1.ini','-i','in2.ini','-o','out1.ini','-o','out2.ini',
                    '-g','gen1.ini','-g','gen2.ini','-c','col1.ini','-c','col2.ini',
                    '-n','my name','-s','file','-l','DEBUG']        
        pargs = handler.get_parsed_arguments(self.log)
        expected = {
                  'INPUTS':['in1.ini','in2.ini'],
                  'OUTPUT':'out2.ini', # 1st value of -o is overwritten
                  'GENERATORS':['gen1.ini','gen2.ini'],
                  'COLLECTORS':['col1.ini','col2.ini'],
                  'NAME': 'my name',
                  'STORAGE': 'file',
                  'LOG_LEVEL': 'DEBUG',
                                    
                  }
        # needed to print the diff 
        self.maxDiff = None
        self.assertDictEqual(pargs, expected)

    def test_application_args_handler_2(self):
        '''Test defined arguments and undefined arguments'''
        handler = ApplicationArgsHandler()
        sys.argv = ['test.py','-i','in1.ini','-i','in2.ini','-o','out1.ini','-o','out2.ini',
                    '-g','gen1.ini','-g','gen2.ini','-c','col1.ini','-c','col2.ini',
                    '-n','my name','-s','file','-l','DEBUG','--key','value']        
        try:
            handler.get_parsed_arguments(self.log)
            self.assertFalse(True, 'Test should fail')
        except:            
            self.assertTrue(True, 'Test failed as expected')
            
    def test_wrapper_args_handler_1(self):
        '''Test defined arguments'''
        handler = WrapperArgsHandler()
        sys.argv = ['test.py','-i','in1.ini','-i','in2.ini','-o','out1.ini','-o','out2.ini',
                    '-g','gen1.ini','-g','gen2.ini','-c','col1.ini','-c','col2.ini',
                    '-n','my name','-s','file','-l','DEBUG','--prefix','mytool.exe','--template','template.tpl']        
        pargs = handler.get_parsed_arguments(self.log)
        expected = {
                  'INPUTS':['in1.ini','in2.ini'],
                  'OUTPUT':'out2.ini', # 1st value of -o is overwritten
                  'GENERATORS':['gen1.ini','gen2.ini'],
                  'COLLECTORS':['col1.ini','col2.ini'],
                  'NAME': 'my name',
                  'STORAGE': 'file',
                  'LOG_LEVEL': 'DEBUG',
                  'PREFIX': 'mytool.exe',
                  'TEMPLATE':'template.tpl'                                    
                  }
        # needed to print the diff 
        self.maxDiff = None
        self.assertDictEqual(pargs, expected)           
            

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()