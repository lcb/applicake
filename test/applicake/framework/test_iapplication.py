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
from applicake.framework.runner import BasicApplicationRunner

class Application(IApplication):

    out_txt = 'my stdout txt'
    err_txt = 'my stderr txt'
    log_txt = 'LOG' 
          
    def main(self,info,log):

        sys.stdout.write(self.out_txt)
        sys.stderr.write(self.err_txt)
        log.debug(self.log_txt)
        return (0,info)

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
        
        
    def test__call__1(self):
        '''Test stream storage in memory '''
        sys.argv = ['test.py','-i',self.input_ini, 
                    '-o',self.output_ini,
                    '-n',self.random_name,'-s','file','-l','DEBUG']
        runner = BasicApplicationRunner()
        application = Application()
        exit_code = runner(sys.argv,application)
        runner.out_stream.seek(0)
        runner.err_stream.seek(0)
        runner.log_stream.seek(0)  
        out = runner.out_stream.read()
        err = runner.err_stream.read()
        log = runner.log_stream.read()      
        assert  out == Application().out_txt
        assert  err == Application().err_txt
        # log contains more that only the log_txt
        assert Application().log_txt in log       
        assert exit_code == 0

    def test__call__2(self):
        '''Test stream storage in files '''
        sys.argv = ['test.py','-i',self.input_ini, 
                    '-o',self.output_ini,
                    '-n',self.random_name,'-s','file','-l','DEBUG']
        runner = BasicApplicationRunner()
        application = Application()
        exit_code = runner(sys.argv,application)
#        assert os.path.exists(runner.info['out_file'])
#        assert os.path.exists(runner.info['err_file'])  
#        assert os.path.exists(runner.info['log_file'])  
        runner.out_stream.seek(0)
        runner.err_stream.seek(0)
        runner.log_stream.seek(0)  
        out = runner.out_stream.read()
        err = runner.err_stream.read()
        log = runner.log_stream.read()      
        assert  out == Application().out_txt
        assert  err == Application().err_txt
        # log contains more that only the log_txt
        assert Application().log_txt in log       
        assert exit_code == 0  
        
    def test_read_inputs__1(self):
        '''Test reading of a single input file '''
        sys.argv = ['test.py','-i',self.input_ini, 
                    '-o',self.output_ini,
                    '-n',self.random_name,'-s','file','-l','DEBUG']                
        runner = BasicApplicationRunner()
        application = Application()
        runner(sys.argv,application)
        info = runner.info
        assert info['COMMENT'] == 'test message'

    def test_read_inputs__2(self):
        '''Test of multiple input files and merging of them'''
        sys.argv = ['test.py','-i',self.input_ini, '-i',self.input_ini2, 
                    '-o',self.output_ini,
                    '-n',self.random_name,'-s','file','-l','DEBUG']                
        runner = BasicApplicationRunner()
        application = Application()
        runner(sys.argv,application)
        assert runner.info['COMMENT'] == ['test message', 'another test message']                                    

if __name__ == "__main__":
    unittest.main()