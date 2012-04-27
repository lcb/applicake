'''
Created on Apr 10, 2012

@author: quandtan
'''
import unittest
from applicake.framework.logger import Logger
from applicake.framework.enums import KeyEnum
from applicake.applications.os.rsync import Rsync
from StringIO import StringIO

class Test(unittest.TestCase):

    #setUp and tearDown are pre-defined test functions
    def setUp(self):
        self.log = Logger.create(level='DEBUG',name='memory_logger',stream=StringIO())
        self.info = {KeyEnum.src_key: '/from/dir /to/dir'}
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
    def test_prepare_run(self):
        command, info = Rsync().prepare_run(self.info, self.log)
        assert command == "rsync -e 'ssh -o PreferredAuthentications=publickey,hostbased' -vrtz -l /from/dir /to/dir"

    def test_validate_run(self):
        run_code, info = Rsync().validate_run(self.info, self.log, 0, self.out_stream, err_stream=None)
        assert run_code == 0
        assert info[KeyEnum.dest_key] == ['/to/dir/file1', '/to/dir/file2', '/to/dir/file3']
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_echo']
    unittest.main()