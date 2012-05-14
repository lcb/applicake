'''
Created on May 14, 2012

@author: quandtan
'''
import unittest
import os
import sys
from pylint.pyreverse import main


class Test(unittest.TestCase):


    def setUp(self):
        self.cwd = os.getcwd()
        os.chdir('../misc/uml') 


    def tearDown(self):
        os.chdir(self.cwd)


    def test_create_umls(self):
        """
        Generate class and package diagrams for applicake
        """
        sys.argv = 'pyreverse -o png -p applicake ../../src/applicake'.split(' ')
        main.Run(sys.argv[1:])



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()