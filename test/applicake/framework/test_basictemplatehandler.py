'''
Created on Apr 23, 2012

@author: quandtan
'''
import os
import shutil
import unittest
from applicake.framework.logger import Logger
from applicake.framework.templatehandler import BasicTemplateHandler
from StringIO import StringIO

class Test(unittest.TestCase):


    def setUp(self):
        self.log_stream = StringIO()
        self.log = Logger(level='DEBUG',name='memory_logger',stream=self.log_stream).logger
        self.cwd = os.getcwd()
        self.tmp_dir = '%s/tmp' % os.path.abspath(os.getcwd())
        os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)
        path = 'template.tpl'
        fh = open(path, 'w+')
        self.var = '$MYVAR'
        fh.write('my template contains a var [%s]' % self.var)
        self.info = {
                     'TEMPLATE':path,
                     'MYVAR': 'value of var'
                     }


    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        os.chdir(self.cwd)


    def test_basic_read_template_1(self):
        '''Test to read template.'''
        template = BasicTemplateHandler().read_template(self.info, self.log)
        expected = 'my template contains a var [%s]' % self.var
        self.assertTrue(template == expected, 'template [%s]\nexpected[%s]' % (template,expected))
    
    def test_basic_read_template_2(self):
        '''Test if reading fails in case info does not contain the 'TEMPLATE' key.'''
        self.info.pop('TEMPLATE')
        try:
            BasicTemplateHandler().read_template(self.info, self.log)
            self.assertTrue(False, 'Test should fail.')
        except:
            self.log_stream.seek(0)
            last_entry = self.log_stream.readlines()[-1]
            contain = "CRITICAL - info does not contain key [%s]: [{'MYVAR': 'value of var'}]" % BasicTemplateHandler().template_key
            self.assertTrue(contain in last_entry, 'last_entry [%s]\ncontain[%s]' % (last_entry,contain))    
    
    def test_basic_replace_vars(self):
        '''Test if template is modified correctly with vars from dictionary.'''
        template = 'my template contains a var [%s]' % self.var
        mod_template = BasicTemplateHandler().replace_vars(self.info, self.log, template)
        expected = 'my template contains a var [value of var]'
        self.assertTrue(mod_template == expected, 'mod_template [%s]\nexpected [%s]' % (mod_template,expected))
        
    
    def test_basic_write_template_1(self):
        '''Test if template is correctly written. '''
        expected = 'my template contains a var [value of var]'
        BasicTemplateHandler().write_template(self.info, self.log, expected)
        path = self.info[BasicTemplateHandler().template_key]
        fh = open(path,'r+')
        content = fh.read()
        self.assertTrue(content == expected, 'content [%s]\nexpected [%s]' % (content,expected))
    
    def test_basic_write_template_2(self):
        '''Test if writing fails in case info does not contain the 'TEMPLATE' key.'''
        expected = 'my template contains a var [value of var]'
        self.info.pop('TEMPLATE')
        try:
            BasicTemplateHandler().write_template(self.info, self.log, expected)
            self.assertTrue(False, 'Test should fail.')
        except:
            self.log_stream.seek(0)
            last_entry = self.log_stream.readlines()[-1]
            contain = "CRITICAL - info does not contain key [%s]: [{'MYVAR': 'value of var'}]" % BasicTemplateHandler().template_key
            self.assertTrue(contain in last_entry, 'last_entry [%s]\ncontain[%s]' % (last_entry,contain))
            
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()