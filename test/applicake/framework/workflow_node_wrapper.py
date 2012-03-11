'''
Created on Mar 6, 2012

@author: quandtan
'''
import os
import random
import shutil
import string
import sys
import unittest
from applicake.framework.app import WorkflowNodeWrapper


class TestNode(WorkflowNodeWrapper):
    
    out_txt = 'my stdout txt'
    err_txt = 'my stderr txt'
    log_txt = 'LOG'    
    
    def prepare_run(self,prefix):
        self.log.debug(self.log_txt)
        return '%s "%s";%s "%s" >&2' % (prefix,self.out_txt,
                               prefix,self.err_txt)
        
    def validate_run(self,run_code):
        if 0 != run_code:
            return run_code
        return 0

class Test(unittest.TestCase):
    """
    Test class for WorkflowNodeWrapper class
    """
    
    def setUp(self):
        # if the log name is not different for all tests, there is a mix-up of messages
        self.random_name = ''.join(random.sample(string.ascii_uppercase + string.digits,20))  
        #create temporary files
        self.cwd = os.getcwd()
        self.tmp_dir = '%s/data' % os.path.abspath(os.getcwd())
        os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)
        self.input_ini = '%s/input.ini' % self.tmp_dir
        self.input_ini = '%s/input.ini' % self.tmp_dir
        f = open(self.input_ini, 'w+')
        f.write('COMMENT=test message')
        f.close()
        self.input_ini2 = '%s/second_input.ini' % self.tmp_dir
        f = open(self.input_ini2, 'w+')
        f.write('COMMENT=another test message')
        f.close()        
        self.output_ini = '%s/output.ini' % self.tmp_dir 

    def tearDown(self):      
        shutil.rmtree(self.tmp_dir)
        os.chdir(self.cwd)   
        
    def test__init__1(self):
        '''Test of stream storage in memory '''
        sys.argv = ['test.py','-i',self.input_ini,'-i',self.input_ini2, 
                    '-o',self.output_ini,'-o',self.output_ini, '-n',self.random_name,
                    '-p','/bin/echo']
        # init the application object (__init__)
        app = TestNode()
        # call the application object as method (__call__)
        exit_code = app(sys.argv)             
        app.out_stream.seek(0)
        app.err_stream.seek(0)
        app.log_stream.seek(0)  
        out = app.out_stream.read()
        err = app.err_stream.read()
        log = app.log_stream.read()      
        # echo adds '\n' to the streams which has to be removed
        assert  out.rstrip() == app.out_txt
        assert  err.rstrip() == app.err_txt
        # log contains more that only the log_txt
        assert app.log_txt in log        
        assert exit_code == 0   
        
    def test__init__2(self):
        sys.argv = ['test.py','-i',self.input_ini,'-i',self.input_ini2, 
                    '-o',self.output_ini,'-o',self.output_ini, '-n',self.random_name,
                    '-p','/bin/echo']
        # init the application object (__init__)
        app = TestNode(storage='file')
        # call the application object as method (__call__)
        exit_code = app(sys.argv)
        assert os.path.exists(app.info['out_file'])
        assert os.path.exists(app.info['err_file'])  
        assert os.path.exists(app.info['log_file'])       
        app.out_stream.seek(0)
        app.err_stream.seek(0)
        app.log_stream.seek(0)  
        out = app.out_stream.read()
        err = app.err_stream.read()
        log = app.log_stream.read()      
        # echo adds '\n' to the streams which has to be removed
        assert  out.rstrip() == app.out_txt
        assert  err.rstrip() == app.err_txt
        # log contains more that only the log_txt
        assert app.log_txt in log      
        assert exit_code == 0         
            
               

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()