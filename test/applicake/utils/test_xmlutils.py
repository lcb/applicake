'''
Created on Apr 11, 2012

@author: quandtan
'''
import unittest
import os
import shutil
from applicake.utils.xmlutils import XmlValidator
from applicake.utils.xmlutils import XmlUtils
from lxml import etree

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
        path = os.path.join(self.tmp_dir,'test.xml')
        fh = open(path,'w+')
        fh.write(self.xml)
        fh.close()
        xml_val = XmlValidator()
        assert True == xml_val.is_wellformed(path)
        
    def test_xml2d(self):        
        dic = {'T': {'a': [{'n': '1'}, {'n': '2'}], 'b': [{'c': [{'x': 'y'}], 'n': '3'}], 'uri': 'boo'}}
        assert dic == XmlUtils.xml2d(etree.XML(self.xml))     
        
    def test_d2xml(self):    
        dic = XmlUtils.xml2d(etree.XML(self.xml))
        root = XmlUtils.d2xml(dic)     
        assert self.xml == etree.tostring(root) 
        elems = root.xpath('//a/@n')
        assert 2 == len(elems)
        assert '1' == elems[0]
        assert '2' == elems[1]  
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_xml_validator']
    unittest.main()