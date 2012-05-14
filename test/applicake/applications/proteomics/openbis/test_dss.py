'''
Created on Apr 10, 2012

@author: quandtan
'''
import unittest
import sys
from applicake.framework.logger import Logger
from applicake.framework.enums import KeyEnum
from applicake.framework.runner import BasicWrapperRunner
from applicake.applications.proteomics.openbis.dss import Dss
from StringIO import StringIO

class Test(unittest.TestCase):

    #setUp and tearDown are pre-defined test functions
    def setUp(self):
        log_stream = StringIO()
        self.log = Logger.create(level='DEBUG',name='memory_logger',stream=log_stream)        
        self.info = {KeyEnum.PREFIX : 'getmsdata',
                     KeyEnum.DATASET_CODE : '20120510111600123-123456',
                     'DATASET_DIR' : '/IMSB/users/schmide/applicake/test/outdir'}
        
    #all methods starting with 'test' tested with unittest
    def test_prepare_run(self):
        command, info = Dss().prepare_run(self.info, self.log)
        print command
        print info

    def test_run(self):
        runner = BasicWrapperRunner()
        wrapper = Dss()
        sys.argv = ['','-i', 'ini.txt', '-o', 'outi.txt', '--PREFIX', 'getmsdata']
        exit_code = runner(sys.argv, wrapper)
        print exit_code
        
    def notyet_test_validate_run(self):
        run_code, info = Dss().validate_run(self.info, self.log, 0)
        assert run_code == 0
        assert info[KeyEnum.DESTINATION] == ['/to/dir/file1', '/to/dir/file2', '/to/dir/file3']
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_echo']
    unittest.main()