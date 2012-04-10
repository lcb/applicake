'''
Created on Apr 10, 2012

@author: quandtan
'''
import unittest
import os
import shutil
import sys
from applicake.framework.runner import WrapperRunner
from applicake.framework.confighandler import ConfigHandler
from applicake.applications.os.echo import Echo  


class Test(unittest.TestCase):


    def setUp(self):
        self.input = 'echo_test.ini'
        self.tmp_dir = '%s/tmp' % os.path.abspath(os.getcwd())
        self.cwd = os.getcwd()
        os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)        
        fh = open(self.input,'w+')
        fh.write("""COMMENT = hello world
STORAGE = file
OUTPUT = /fake/output.ini 
LOG_LEVEL = INFO
BASEDIR = /tmp
""")
        fh.close()
        self.output = 'input.ini'

    def tearDown(self):
        os.remove(self.input)
        os.remove(self.output)
        shutil.rmtree(self.tmp_dir)
        os.chdir(self.cwd)


    def test_echo(self):
        runner = WrapperRunner()
        wrapper = Echo()
        sys.argv = ['run_echo.py', '-i', self.input, '-o',self.output]
        exit_code = runner(sys.argv,wrapper)  
        assert 0 == exit_code      
        config = ConfigHandler().read(self.output)
        print config
        outfile = os.path.join(config['WORKDIR'],config['CREATED_FILES'][0])        
        assert 'hello world\n' == open(outfile,'r').read()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_echo']
    unittest.main()