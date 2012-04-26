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
from applicake.applications.os.copier import Copier
from StringIO import StringIO
from tempfile import mkdtemp

class test_copier(unittest.TestCase):

    #setUp and tearDown are pre-defined test functions
    def setUp(self):
        self.copier = Copier()

        self.log = Logger(level='DEBUG',name='memory_logger',stream=StringIO()).logger
        self.info = {'COPY': '/from/dir /to/dir'}
        self.out_stream = StringIO()
        self.out_stream.write("""building file list ... done
file1
file2
file3

sent 82 bytes  received 42 bytes  248.00 bytes/sec
total size is 0  speedup is 0.00
""")
        self.out_stream.seek(0)
        
    #all methods starting wiht 'test' tested with unittest
    def test_preparerun(self):
        command, info = self.copier.prepare_run(self.info, self.log)
        assert command == "rsync -e 'ssh -o PreferredAuthentications=publickey,hostbased' -vrtz -l /from/dir /to/dir"

    def test_validaterun(self):
        run_code, info = self.copier.validate_run(self.info, self.log, 0, self.out_stream, err_stream=None)
        assert run_code == 0
        assert info['COPYOUTPUT'] == ['/to/dir/file1', '/to/dir/file2', '/to/dir/file3']
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_echo']
    unittest.main()