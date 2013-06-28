'''
Created on Apr 23, 2012

@author: quandtan
'''
import os
import shutil
import unittest
from StringIO import StringIO

from applicake.framework.keys import Keys
from applicake.framework.logger import Logger
from applicake.framework.templatehandler import BasicTemplateHandler


class Test(unittest.TestCase):
    def setUp(self):
        self.log_stream = StringIO()
        self.log = Logger.create(level='DEBUG', name='memory_logger', stream=self.log_stream)
        self.cwd = os.getcwd()
        self.tmp_dir = '%s/tmp' % os.path.abspath(os.getcwd())
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)
        path = 'template.tpl'
        fh = open(path, 'w+')
        self.var = '$MyVar'
        fh.write('my template contains a var $MyVar')
        self.info = {Keys.TEMPLATE: path, 'MyVar': 'valueofvar'}

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        os.chdir(self.cwd)


    def test_basic_read_template_1(self):
        '''Test to read template.'''
        template, info = BasicTemplateHandler().read_template(self.info, self.log)
        expected = 'my template contains a var $MyVar'
        self.assertTrue(template == expected, 'template [%s]\nexpected[%s]' % (template, expected))

    def test_basic_read_template_2(self):
        '''Test if reading fails in case info does not contain the 'TEMPLATE' key.'''
        self.info.pop('TEMPLATE')
        try:
            BasicTemplateHandler().read_template(self.info, self.log)
            self.assertTrue(False, 'Test should fail.')
        except:
            assert True

    def test_basic_modify_template(self):
        '''Test if template is modified correctly with vars from dictionary.'''
        template = 'my template contains a var [$MyVar] ${MyVar}2'
        mod_template, info = BasicTemplateHandler().modify_template(self.info, self.log, template)
        expected = 'my template contains a var [valueofvar] valueofvar2'
        self.assertTrue(mod_template == expected, 'mod_template [%s]\nexpected [%s]' % (mod_template, expected))

    def test_basic_write_template_1(self):
        '''Test if template is correctly written. '''
        expected = 'my template contains a var [value of var]'
        BasicTemplateHandler().write_template(self.info, self.log, expected)
        path = self.info[Keys.TEMPLATE]
        fh = open(path, 'r+')
        content = fh.read()
        self.assertTrue(content == expected, 'content [%s]\nexpected [%s]' % (content, expected))

    def test_basic_write_template_2(self):
        '''Test if writing fails in case info does not contain the 'TEMPLATE' key.'''
        expected = 'my template contains a var [value of var]'
        self.info.pop('TEMPLATE')
        try:
            BasicTemplateHandler().write_template(self.info, self.log, expected)
            self.assertTrue(False, 'Test should fail.')
        except:
            assert True


if __name__ == "__main__":
    unittest.main()
