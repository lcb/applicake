'''
Created on Apr 10, 2012

@author: quandtan
'''
import unittest
import os
import shutil
import sys
from applicake.framework.confighandler import ConfigHandler
from applicake.framework.logger import Logger
from applicake.framework.runner import BasicWrapperRunner
from applicake.applications.os.echo import Echo  
from StringIO import StringIO

class Test(unittest.TestCase):


    def setUp(self):
        log_stream = StringIO()
        self.log = Logger(level='DEBUG',name='memory_logger',stream=log_stream).logger
        self.input = 'echo_test.ini'
        self.tmp_dir = '%s/tmp' % os.path.abspath(os.getcwd())
        self.cwd = os.getcwd()
        os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)        
        fh = open(self.input,'w+')
        fh.write("""COMMENT = hello world
PREFIX = /bin/echo        
STORAGE = file
OUTPUT = /fake/output.ini 
LOG_LEVEL = INFO
BASEDIR = /tmp
""")
        fh.close()
        self.output = 'output.ini'

    def tearDown(self):
        os.remove(self.input)
        os.remove(self.output)
        shutil.rmtree(self.tmp_dir)
        os.chdir(self.cwd)


    def test_echo(self):
        runner = BasicWrapperRunner()
        wrapper = Echo()
        sys.argv = ['run_echo.py', '-i', self.input, '-o',self.output]
        exit_code = runner(sys.argv,wrapper)  
        assert 0 == exit_code      
        config = ConfigHandler().read(self.log,self.output)
        print config
        outfile = config['CREATED_FILES'][0]       
        assert 'hello world\n' == open(outfile,'r').read()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_echo']
    unittest.main()