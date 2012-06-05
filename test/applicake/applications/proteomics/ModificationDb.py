'''
Created on Jun 5, 2012

@author: quandtan
'''
import unittest
from applicake.applications.proteomics.modifications import ModificationDb


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_get(self):
        c = ModificationDb()
        self.assertEqual(c.get('Phospho (STY)', 'xtandem'),
                         '79.966331@S,79.966331@T,79.966331@Y',
                         None)
        try:
            c.get('blabla', 'xtandem')
            assert False
        except:
            assert True
            
        try:
            c.get('Phospho (STY)', 'blabla')
            assert False
        except:
            assert True   


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_get']
    unittest.main()