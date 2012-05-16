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
from applicake.framework.runner import WrapperRunner
from applicake.applications.os.echo import Echo  
from StringIO import StringIO

class Test(unittest.TestCase):


    def setUp(self):
        log_stream = StringIO()
        self.log = Logger.create(level='DEBUG',name='memory_logger',stream=log_stream)
        self.input = 'echo_test.ini'
        self.tmp_dir = '%s/tmp' % os.path.abspath(os.getcwd())
        self.cwd = os.getcwd()
        os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)        
        fh = open(self.input,'w+')
        fh.write("""%s = hello world
%s = /bin/echo        
%s = file
%s = /fake/output.ini 
%s = INFO
%s = /tmp
""" % (Echo.COMMENT,Echo.PREFIX,Echo.STORAGE,Echo.OUTPUT,Echo.LOG_LEVEL, Echo.BASEDIR))
        fh.close()
        self.output = 'myoutput.ini'

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        os.chdir(self.cwd)
    

    def test_prepare_run(self):
        app = Echo()
        org_info = {app.PREFIX:'/bin/echo',app.COMMENT:'hello world'}
        comment, info = Echo().prepare_run(org_info, self.log)
        assert comment == '/bin/echo "hello world"'
        assert org_info == info
        
        

    def test_echo_1(self):
        """Test with input.ini"""
        runner = WrapperRunner()
        wrapper = Echo()
        sys.argv = ['run_echo.py', '-i', self.input, '-o',self.output, '--%s' % Echo.LOG_LEVEL, 'DEBUG']
        exit_code = runner(sys.argv,wrapper)  
        assert 0 == exit_code      
        config = ConfigHandler().read(self.log,self.output)
        print config
        outfile = config[wrapper.CREATED_FILES][0]       
        assert 'hello world\n' == open(outfile,'r').read()
        errfile = config[wrapper.CREATED_FILES][1]
        assert os.path.getsize(errfile) == 0
        logfile = config[wrapper.CREATED_FILES][2]
        assert os.path.getsize(logfile) >0
        

    def test_echo_2(self):
        '''Test without input.ini '''
        runner = WrapperRunner()
        wrapper = Echo()
        expected = 'hello world'
        sys.argv = ['run_echo.py', '--%s' % wrapper.COMMENT,expected, '--%s' % wrapper.PREFIX,'/bin/echo']
        exit_code = runner(sys.argv,wrapper)  
        assert 0 == exit_code      
        runner.out_stream.seek(0)
        found = runner.out_stream.read()
        print runner.info
        self.assertTrue(expected == found.rstrip(),'expected [%s]\nfound [%s]' % (expected,found))       

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_echo']
    unittest.main()