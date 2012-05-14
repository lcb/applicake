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
from applicake.framework.enums import KeyEnum
from applicake.framework.interfaces import IWrapper
from applicake.framework.runner import BasicWrapperRunner
from applicake.applications.os.echo import Echo


class Wrapper(IWrapper):
    
    out_txt = 'my stdout txt'
    err_txt = 'my stderr txt'
    log_txt = 'LOG'    
    
    def prepare_run(self,info,log):
        log.debug(self.log_txt)
        prefix = info[KeyEnum.PREFIX]
        command = '%s "%s";%s "%s" >&2' % (prefix,self.out_txt,
                               prefix,self.err_txt)
        return (command,info)
        
    def validate_run(self,info,log,run_code, out_stream, err_stream):
        exit_code = None
        if 0 != run_code:
            exit_code = run_code
        else:
            exit_code = 0
        return (exit_code,info)

class Test(unittest.TestCase):
    """
    Test class for BasicWrapperRunner class
    """
    
    def setUp(self):
        # if the log name is not different for all tests, there is a mix-up of messages
        self.random_name = ''.join(random.sample(string.ascii_uppercase + string.digits,20))  
        #create temporary files
        self.cwd = os.getcwd()
        self.tmp_dir = '%s/tmp' % os.path.abspath(os.getcwd())
        os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)
        self.input_ini = '%s/input.ini' % self.tmp_dir
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
        '''Test of stream storage in memory '''
        sys.argv = ['test.py','-i',self.input_ini,'-i',self.input_ini2, 
                    '-o',self.output_ini,'-o',self.output_ini, '--NAME',self.random_name,
                    '--PREFIX','/bin/echo','--STORAGE','memory','--LOG_LEVEL','DEBUG']

        runner = BasicWrapperRunner()
        wrapper = Wrapper()
        exit_code = runner(sys.argv,wrapper)   
        
        runner.out_stream.seek(0)
        runner.err_stream.seek(0)
        runner.log_stream.seek(0)  
        out = runner.out_stream.read()
        err = runner.err_stream.read()
        log = runner.log_stream.read()      
        self.assertTrue(out.rstrip() == Wrapper().out_txt,'found [%s]\nexpected [%s]' % (out,Wrapper().out_txt))
        self.assertTrue(err.rstrip() == Wrapper().err_txt,'found [%s]\nexpected [%s]' % (err,Wrapper().err_txt))
        # log contains more that only the log_txt
        self.assertTrue(Wrapper().log_txt in log,'found [%s]\ncontains [%s]' % (log,Wrapper().log_txt))             
        assert exit_code == 0        

    def test__call__2(self):
        '''Test stream storage in files '''
        sys.argv = ['test.py','-i',self.input_ini,'-i',self.input_ini2, 
                    '-o',self.output_ini,'-o',self.output_ini, '--NAME',self.random_name,
                    '--PREFIX','/bin/echo','--STORAGE','file','--LOG_LEVEL','DEBUG']
        runner = BasicWrapperRunner()
        wrapper = Wrapper()
        exit_code = runner(sys.argv,wrapper)
        
        out = open('%s.out' % self.random_name,'r+').read()
        err = open('%s.err' % self.random_name,'r+').read()
        log = open('%s.log' % self.random_name,'r+').read()  
        # problem is the unclosed stream   
        self.assertTrue(out.rstrip() == wrapper.out_txt,'found [%s]\nexpected [%s]' % (out,wrapper.out_txt))
        self.assertTrue(err.rstrip() == wrapper.err_txt,'found [%s]\nexpected [%s]' % (err,wrapper.err_txt))
        # log contains more that only the log_txt
        self.assertTrue(wrapper.log_txt in log,'found [%s]\ncontains [%s]' % (log,wrapper.log_txt))
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
            
    def test__call__3(self):
        '''Test stream storage in files with os.echo.Echo  '''
        sys.argv = ['test.py','-i',self.input_ini,'-i',self.input_ini2, 
                    '-o',self.output_ini,'-o',self.output_ini, '--NAME',self.random_name,
                    '--PREFIX','/bin/echo','--STORAGE','file','--LOG_LEVEL','DEBUG']
        runner = BasicWrapperRunner()
        wrapper = Echo()
        exit_code = runner(sys.argv,wrapper)
        
        out = open('%s.out' % self.random_name,'r+').read()
        log = open('%s.log' % self.random_name,'r+').read()  
        # problem is the unclosed stream   
        expected = '%s' % ['test message', 'another test message']
        self.assertTrue(out.rstrip() == expected,'found [%s]\nexpected [%s]' % (out.rstrip(),expected))
        # log contains more that only the log_txt
        self.assertTrue(Wrapper().log_txt in log,'found [%s]\ncontains [%s]' % (log,Wrapper().log_txt))
        runner.out_stream.seek(0)
        runner.log_stream.seek(0)  
        out_stream = runner.out_stream.read()
        log_stream = runner.log_stream.read()        
        self.assertTrue(out == out_stream,'[%s]\n[%s]' % (out,out_stream))    
        self.assertTrue(log_stream == log,'[%s]\n[%s]' % (log,log_stream))              
        assert exit_code == 0         
                       

if __name__ == "__main__":
    unittest.main()