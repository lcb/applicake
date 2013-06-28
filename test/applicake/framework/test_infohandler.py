'''
Created on Apr 22, 2012

@author: loblum
'''
import unittest
import os
import shutil

from applicake.framework.keys import Keys
from applicake.framework.informationhandler import *
from applicake.framework.logger import Logger


class Test(unittest.TestCase):
    def setUp(self):
        self.cwd = os.getcwd()
        self.tmp_dir = '%s/tmp' % os.path.abspath(os.getcwd())
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
        os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)
        self.input_ini = '%s/input.ini' % self.tmp_dir
        f = open(self.input_ini, 'w+')
        f.write("COMMENT=test handler")
        f.close()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        os.chdir(self.cwd)

    def test_IniInfoHandler(self):
        basic = IniInformationHandler()
        log = Logger.create()
        pargs = {Keys.INPUT: "input.ini", Keys.OUTPUT: "output.ini"}
        read_info = basic.get_info(log, pargs)
        merge_info = DictUtils.merge(log, pargs, read_info)
        assert merge_info[Keys.COMMENT] == "test handler"
        basic.write_info(merge_info, log)
        assert os.path.exists(self.tmp_dir + "/output.ini")
        assert os.path.getsize(self.tmp_dir + "/output.ini") > 1


if __name__ == "__main__":
    unittest.main()
