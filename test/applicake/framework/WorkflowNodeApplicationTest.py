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
from applicake.framework.app import WorkflowNodeApplication


class TestNode(WorkflowNodeApplication):
    def main(self):
        print 'info [%s]' % self.info
        return 0

class Test(unittest.TestCase):


    def setUp(self):
        # if the log name is not different for all tests, there is a mix-up of messages
        self.random_name = ''.join(random.sample(string.ascii_uppercase + string.digits,20))  
        #create temporary files
        self.tmp_dir = '%s/data' % os.path.abspath(os.curdir)
        os.mkdir(self.tmp_dir)
        self.input_ini = '%s/input.ini' % self.tmp_dir
        f = open(self.input_ini, 'w+')
        f.close()

    def tearDown(self):        
        shutil.rmtree(self.tmp_dir)
        

    def test_define_arguments__1(self):
        sys.argv = ['test.py','-i',self.input_ini, '-o','data/output.ini']
        # init the application object (__init__)
        app = TestNode(use_filesystem=False)
        # call the application object as method (__call__)
        exit_code = app(sys.argv)
        inputs = app.info['inputs']
        outputs = app.info['outputs']
        name = app.info['name']
        assert isinstance(inputs, (list))
        assert len(inputs) == 1
        assert isinstance(outputs, (list))
        assert len(outputs) == 1
        assert name == 'testnode' 
        assert exit_code == 0


    def test_define_arguments__2(self):
        sys.argv = ['test.py','-i',self.input_ini, '-o','data/output.ini', '-n', self.random_name]
        # init the application object (__init__)
        app = TestNode(use_filesystem=False)
        # call the application object as method (__call__)
        exit_code = app(sys.argv)
        name = app.info['name']
        assert name == self.random_name.lower()
        assert exit_code == 0
        
    def test_define_arguments__3(self):
        try: 
            sys.argv = ['test.py','-i','-i',self.input_ini, '-o','%s/output.ini' % self.tmp_dir,
                         '-n', self.random_name]
            # init the application object (__init__)
            app = TestNode(use_filesystem=False)
            # call the application object as method (__call__)
            app(sys.argv)            
        except:
            self.assertTrue(True, 'Test failed as expected')
            return
        self.fail("""This test should fail because the following argument combination 
        [%s] is not allowed""" % sys.argv)    
        
    def test_define_arguments__4(self):
        try: 
            sys.argv = ['test.py','-i',self.input_ini, '-o','-o','%s/output.ini' % self.tmp_dir,
                         '-n', self.random_name]
            # init the application object (__init__)
            app = TestNode(use_filesystem=False)
            # call the application object as method (__call__)
            app(sys.argv)            
        except:
            self.assertTrue(True, 'Test failed as expected')
            return
        self.fail("""This test should fail because the following argument combination 
        [%s] is not allowed""" % sys.argv)        
                  
    def test_define_arguments__5(self):
        try: 
            sys.argv = ['test.py','-i',self.input_ini, '-o','%s/output.ini' % self.tmp_dir,
                         '-n','-n', self.random_name]
            # init the application object (__init__)
            app = TestNode(use_filesystem=False)
            # call the application object as method (__call__)
            app(sys.argv)            
        except:
            self.assertTrue(True, 'Test failed as expected')
            return
        self.fail("""This test should fail because the following argument combination 
        [%s] is not allowed""" % sys.argv)  

    def test_define_arguments__6(self):
        sys.argv = ['test.py','-i',self.input_ini,'-i',self.input_ini, 
                    '-o','%s/output.ini' % self.tmp_dir,'-o','%s/output.ini' % self.tmp_dir,
                    '-n',self.random_name]
        # init the application object (__init__)
        app = TestNode(use_filesystem=False)
        # call the application object as method (__call__)
        exit_code = app(sys.argv)
        inputs = app.info['inputs']
        outputs = app.info['outputs']
        name = app.info['name']
        assert isinstance(inputs, (list))
        assert len(inputs) == 2
        assert isinstance(outputs, (list))
        assert len(outputs) == 2
        assert name == self.random_name.lower() 
        assert exit_code == 0        
                       

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()