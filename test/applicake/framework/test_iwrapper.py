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
from applicake.framework.interfaces import IWrapper
from applicake.framework.runner import WrapperRunner


class Wrapper(IWrapper):
    
    out_txt = 'my stdout txt'
    err_txt = 'my stderr txt'
    log_txt = 'LOG'    
    
    def prepare_run(self,info,log):
        log.debug(self.log_txt)
        prefix = info['prefix']
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
    Test class for WrapperRunner class
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
        
    def test__init__1(self):
        '''Test of stream storage in memory '''
        sys.argv = ['test.py','-i',self.input_ini,'-i',self.input_ini2, 
                    '-o',self.output_ini,'-o',self.output_ini, '-n',self.random_name,
                    '-p','/bin/echo','-s','memory','-l','DEBUG']

        runner = WrapperRunner()
        wrapper = Wrapper()
        exit_code = runner(sys.argv,wrapper)          
        runner.out_stream.seek(0)
        runner.err_stream.seek(0)
        runner.log_stream.seek(0)  
        out = runner.out_stream.read()
        err = runner.err_stream.read()
        log = runner.log_stream.read()      
        # echo adds '\n' to the streams which has to be removed
        assert  out.rstrip() == wrapper.out_txt
        assert  err.rstrip() == wrapper.err_txt
        # log contains more that only the log_txt
        assert wrapper.log_txt in log        
        assert exit_code == 0   
        
    def test__init__2(self):
        sys.argv = ['test.py','-i',self.input_ini,'-i',self.input_ini2, 
                    '-o',self.output_ini,'-o',self.output_ini, '-n',self.random_name,
                    '-p','/bin/echo','-s','file','-l','DEBUG']
        runner = WrapperRunner()
        wrapper = Wrapper()
        exit_code = runner(sys.argv,wrapper)
#        assert os.path.exists(runner.info['out_file'])
#        assert os.path.exists(runner.info['err_file'])  
#        assert os.path.exists(runner.info['log_file'])       
        runner.out_stream.seek(0)
        runner.err_stream.seek(0)
        runner.log_stream.seek(0)  
        out = runner.out_stream.read()
        err = runner.err_stream.read()
        log = runner.log_stream.read()      
        # echo adds '\n' to the streams which has to be removed
        assert  out.rstrip() == wrapper.out_txt
        assert  err.rstrip() == wrapper.err_txt
        # log contains more that only the log_txt
        assert wrapper.log_txt in log      
        assert exit_code == 0         
            
               

if __name__ == "__main__":
    unittest.main()