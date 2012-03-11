'''
Created on Mar 6, 2012

@author: quandtan
'''

import cStringIO
import logging
import os
import random
import shutil
import string
import sys
import unittest
from applicake.framework.app import WorkflowNodeApplication

class TestNode(WorkflowNodeApplication):

    out_txt = 'my stdout txt'
    err_txt = 'my stderr txt'
    log_txt = 'LOG' 
          
    def main(self):
        #print self.out_txt
        sys.stdout.write(self.out_txt)
        sys.stderr.write(self.err_txt)
        self.log.debug(self.log_txt)
        return 0

class Test(unittest.TestCase):


    def setUp(self):
        # if the log name is not different for all tests, there is a mix-up of messages
        self.random_name = ''.join(random.sample(string.ascii_uppercase + string.digits,20))  
        #create temporary files
        self.cwd = os.getcwd()
        self.tmp_dir = '%s/data' % os.path.abspath(os.getcwd())
        os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)
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
        ''' Test required command line arguments'''
        sys.argv = ['test.py','-i',self.input_ini, '-o',self.output_ini]
        # init the application object (__init__)
        app = TestNode()
        # call the application object as method (__call__)
        exit_code = app(sys.argv)
        inputs = app.info['inputs']
        outputs = app.info['output']
        name = app.info['name']
        assert isinstance(inputs, (list))
        assert len(inputs) == 1
        assert not isinstance(outputs, (list))
        assert len(name)>0       
        assert exit_code == 0 


    def test__init__2(self):
        ''' Test optional name argument'''
        sys.argv = ['test.py','-i',self.input_ini, '-o',self.output_ini, '-n', self.random_name]
        # init the application object (__init__)
        app = TestNode()
        # call the application object as method (__call__)
        exit_code = app(sys.argv)
        name = app.info['name']
        assert name == self.random_name.lower()      
        assert exit_code == 0 
        
    def test__init__3(self):
        ''' Test required input arguments (not correctly defined)'''
        try: 
            sys.argv = ['test.py','-i','-i',self.input_ini, '-o',self.output_ini,
                         '-n', self.random_name]
            # init the application object (__init__)
            app = TestNode(storage='memory')
            # call the application object as method (__call__)
            app(sys.argv)            
        except:
            self.assertTrue(True, 'Test failed as expected')
            return
        self.fail("""This test should fail because the following argument combination 
        [%s] is not allowed""" % sys.argv)    
        
    def test__init__4(self):
        ''' Test required output arguments (not correctly defined)'''
        try: 
            sys.argv = ['test.py','-i',self.input_ini, '-o','-o',self.output_ini,
                         '-n', self.random_name]
            # init the application object (__init__)
            app = TestNode()
            # call the application object as method (__call__)
            app(sys.argv)            
        except:
            self.assertTrue(True, 'Test failed as expected')
            return
        self.fail("""This test should fail because the following argument combination 
        [%s] is not allowed""" % sys.argv)        
                  
    def test__init__5(self):
        ''' Test optional name arguments (not correctly set)'''
        try: 
            sys.argv = ['test.py','-i',self.input_ini, '-o',self.output_ini,
                         '-n','-n', self.random_name]
            # init the application object (__init__)
            app = TestNode(storage='memory')
            # call the application object as method (__call__)
            app(sys.argv)            
        except:
            self.assertTrue(True, 'Test failed as expected')
            return
        self.fail("""This test should fail because the following argument combination 
        [%s] is not allowed""" % sys.argv)  

    def test__init__6(self):
        ''' Test all arguments (multiple times set)'''
        sys.argv = ['test.py','-i',self.input_ini,'-i',self.input_ini2, 
                    '-o',self.output_ini,'-o',self.output_ini,
                    '-n',self.random_name]
        # init the application object (__init__)
        app = TestNode()
        # call the application object as method (__call__)
        exit_code = app(sys.argv)
        inputs = app.info['inputs']
        outputs = app.info['output']
        name = app.info['name']
        assert isinstance(inputs, (list))
        assert len(inputs) == 2
        assert not isinstance(outputs, (list))
        assert name == self.random_name.lower()  
        app.out_stream.seek(0)
        app.err_stream.seek(0)
        app.log_stream.seek(0)  
        out = app.out_stream.read()
        err = app.err_stream.read()
        log = app.log_stream.read()      
        assert  out == app.out_txt
        assert  err == app.err_txt
        # log contains more that only the log_txt
        assert app.log_txt in log        
        assert exit_code == 0                             

    def test__init__7(self):
        '''Test of stream storage in memory '''
        sys.argv = ['test.py','-i',self.input_ini, 
                    '-o',self.output_ini,
                    '-n',self.random_name]
        # init the application object (__init__)        
        app = TestNode(storage='file')
        # call the application object as method (__call__)
        exit_code = app(sys.argv)
        app.out_stream.seek(0)
        app.err_stream.seek(0)
        app.log_stream.seek(0)  
        out = app.out_stream.read()
        err = app.err_stream.read()
        log = app.log_stream.read()      
        assert  out == app.out_txt
        assert  err == app.err_txt
        # log contains more that only the log_txt
        assert app.log_txt in log       
        assert exit_code == 0

    def test__init__8(self):
        '''Test of stream storage in files '''
        sys.argv = ['test.py','-i',self.input_ini, 
                    '-o',self.output_ini,
                    '-n',self.random_name]
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
        assert  out == app.out_txt
        assert  err == app.err_txt
        # log contains more that only the log_txt
        assert app.log_txt in log       
        assert exit_code == 0  
        
    def test_read_inputs__1(self):
        '''Test reading of a single input file '''
        sys.argv = ['test.py','-i',self.input_ini, 
                    '-o',self.output_ini,
                    '-n',self.random_name]                
        app = TestNode(storage='file') 
        exit_code = app(sys.argv)
        assert app.config.get() == {'COMMENT': ['test message']}

    def test_read_inputs__2(self):
        '''Test of multiple input files and merging of them'''
        sys.argv = ['test.py','-i',self.input_ini, '-i',self.input_ini2, 
                    '-o',self.output_ini,
                    '-n',self.random_name]                
        app = TestNode(storage='file') 
        exit_code = app(sys.argv)
        assert app.config.get() == {'COMMENT': ['test message', 'another test message']}                                    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()