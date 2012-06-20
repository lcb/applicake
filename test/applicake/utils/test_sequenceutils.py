'''
Created on Jun 20, 2012

@author: quandtan
'''
import unittest
from applicake.utils.sequenceutils import SequenceUtils


class Test(unittest.TestCase):


    def test_get_flatten_sequence(self):
        assert SequenceUtils.get_flatten_sequence([1, 2, [3,4], (5,6)]) == [1,2,3,4,5,6]
        assert SequenceUtils.get_flatten_sequence([[[1,2,3], (42,None)], [4,5], [6], 7, (8,9,10)]) == [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]  
        
    def test_unify(self):
        assert SequenceUtils.unify([1,1,1,1]) == [1]
        assert SequenceUtils.unify([1,1,1,1],reduce=True) == 1
        assert SequenceUtils.unify([1,1,2,2,3]) == [1,2,3]

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_get_flatten_sequence']
    unittest.main()