'''
Created on Apr 11, 2012

@author: quandtan
'''
import unittest
import os
import shutil
from applicake.utils.xmlutils import XmlValidator


class Test(unittest.TestCase):
    def setUp(self):
        self.xml = """<T uri="boo"><a n="1"/><a n="2"/><b n="3"><c x="y"/></b></T>"""
        self.cwd = os.getcwd()
        self.tmp_dir = '%s/tmp' % os.path.abspath(os.getcwd())
        os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)


    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        os.chdir(self.cwd)


    def test_xml_validator(self):
        path = os.path.join(self.tmp_dir, 'test.xml')
        fh = open(path, 'w+')
        fh.write(self.xml)
        fh.close()
        xml_val = XmlValidator()
        assert True == xml_val.is_wellformed(path)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_xml_validator']
    unittest.main()
