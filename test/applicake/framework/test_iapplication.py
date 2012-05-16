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
from applicake.framework.interfaces import IApplication
from applicake.framework.runner import ApplicationRunner

class Application(IApplication):

    out_txt = 'my stdout txt'
    err_txt = 'my stderr txt'
    log_txt = 'LOG' 
          
    def main(self,info,log):

        sys.stdout.write(self.out_txt)
        sys.stderr.write(self.err_txt)
        log.debug(self.log_txt)
        return (0,info)
    
    def set_args(self,log,args_handler):
        return args_handler

class Test(unittest.TestCase):


    def setUp(self):
        # if the log name is not different for all tests, there is a mix-up of messages
        self.random_name = ''.join(random.sample(string.ascii_uppercase + string.digits,20))  
        #create temporary files
        self.cwd = os.getcwd()
        self.tmp_dir = '%s/tmp' % os.path.abspath(os.getcwd())
        os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)
        self.input_ini = '%s/input.ini' % self.tmp_dir
        f = open(self.input_ini, 'w+')
        f.write("""COMMENT=test message
        STORAGE = memory
        LOG_LEVEL = DEBUG
        OUTPUT = output.ini
        BASEDIR = /tmp""")
        f.close()
        self.input_ini2 = '%s/second_input.ini' % self.tmp_dir
        f = open(self.input_ini2, 'w+')
        f.write("""COMMENT=another test message
        STORAGE = memory
        LOG_LEVEL = DEBUG
        OUTPUT = output.ini
        BASEDIR = /tmp""")
        f.close()        
        self.output_ini = '%s/output.ini' % self.tmp_dir 

    def tearDown(self):      
        shutil.rmtree(self.tmp_dir)
        os.chdir(self.cwd)
        
        
    def test__iapplication__1(self):
        '''Test stream storage in memory '''
        sys.argv = ['test.py','-i',self.input_ini, 
                    '-o',self.output_ini,
                    '--NAME',self.random_name,'--STORAGE','memory','--LOG_LEVEL','DEBUG']
        runner = ApplicationRunner()
        application = Application()
        exit_code = runner(sys.argv,application)
        runner.out_stream.seek(0)
        runner.err_stream.seek(0)
        runner.log_stream.seek(0)  
        out = runner.out_stream.read()
        err = runner.err_stream.read()
        log = runner.log_stream.read()      
        self.assertTrue(out == Application().out_txt,'found [%s]\nexpected [%s]' % (out,Application().out_txt))
        self.assertTrue(err == Application().err_txt,'found [%s]\nexpected [%s]' % (err,Application().err_txt))
        # log contains more that only the log_txt
        self.assertTrue(Application().log_txt in log,'found [%s]\ncontains [%s]' % (log,Application().log_txt))             
        assert exit_code == 0

    def test__iapplication__2(self):
        '''Test stream storage in files '''
        sys.argv = ['test.py','-i',self.input_ini, 
                    '-o',self.output_ini,
                    '--NAME',self.random_name,'--STORAGE','file','--LOG_LEVEL','DEBUG']
        runner = ApplicationRunner()
        application = Application()
        exit_code = runner(sys.argv,application)
        out = open('%s.out' % os.path.join(os.getcwd(),self.random_name),'r+').read()
        err = open('%s.err' % self.random_name,'r+').read()
        log = open('%s.log' % self.random_name,'r+').read()  
        # problem is the unclosed stream   
        self.assertTrue(out == Application().out_txt,'found [%s]\nexpected [%s]' % (out,Application().out_txt))
        self.assertTrue(err == Application().err_txt,'found [%s]\nexpected [%s]' % (err,Application().err_txt))
        # log contains more that only the log_txt
        self.assertTrue(Application().log_txt in log,'found [%s]\ncontains [%s]' % (log,Application().log_txt))
        runner.out_stream.seek(0)
        runner.err_stream.seek(0)
        runner.log_stream.seek(0)  
        out_stream = runner.out_stream.read()
        err_stream = runner.err_stream.read()
        log_stream = runner.log_stream.read()          
        self.assertTrue(out == out_stream,'[%s]\n[%s]' % (out,out_stream))
        self.assertTrue(err == err_stream,'[%s]\n[%s]' % (err,err_stream))    
        self.assertTrue(log_stream == log,'[%s]\n[%s]' % (log,log_stream))          
        assert exit_code == 0  
        
    def test_iapplication__3(self):
        '''Test reading of a single input file '''
        sys.argv = ['test.py','-i',self.input_ini, 
                    '-o',self.output_ini,
                    '-n',self.random_name,'-s','file','-l','DEBUG']                
        runner = ApplicationRunner()
        application = Application()
        runner(sys.argv,application)
        info = runner.info
        assert info['COMMENT'] == 'test message'

    def test_iapplication__4(self):
        '''Test of multiple input files and merging of them'''
        sys.argv = ['test.py','-i',self.input_ini, '-i',self.input_ini2, 
                    '-o',self.output_ini,
                    '-n',self.random_name,'-s','file','-l','DEBUG']                
        runner = ApplicationRunner()
        application = Application()
        runner(sys.argv,application)
        assert runner.info['COMMENT'] == ['test message', 'another test message']    
        
                                        
    def test_iapplication__5(self):
        '''Test if output.ini is created'''
        sys.argv = ['','-i',self.input_ini, '-i',self.input_ini2, 
                    '-o',self.output_ini,
                    '-n',self.random_name,'-s','file','-l','DEBUG']                
        runner = ApplicationRunner()
        application = Application()
        runner(sys.argv,application)
        assert os.path.exists(self.output_ini)
        assert os.path.getsize(self.output_ini)
if __name__ == "__main__":
    unittest.main()