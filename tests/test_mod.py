#!/usr/bin/env python2.7

import unittest
import sys

from appliapps.tpp.searchengines.modifications import genmodstr_to_engine


class Test(unittest.TestCase):
    def test_mod(self):
        static, var, _ = genmodstr_to_engine("Carbamidomethyl (C);; Biotin(K) ;",
                                             "300/300.1 (STY);Label:13C(6)15N(4) (H)",
                                             "Myrimatch")
        print static, var
        self.assertEqual(static,"C 57.021464 K 226.077598")
        self.assertEqual(var,"[STY] * 300.000000 [H] * 10.008269")
        with self.assertRaises(Exception):
            genmodstr_to_engine("Doesnotexist (C)", "", "Myrimatch")


if __name__ == "__main__":
    if len(sys.argv) > 1 and 'test' not in sys.argv[1]:
        mod = sys.argv[1]
        print "Testing modification '%s'" % mod
        try:
            for i in ['XTandem', 'Omssa', 'Myrimatch', 'Comet']:
                genmodstr_to_engine("", mod, i)
            # print out one example to show masses. myri varmod is most compact
            _, p, _ = genmodstr_to_engine("", mod, 'Comet')
            print p,_
            print "OK"
        except Exception, e:
            raise
            print "ERROR"
            print e.message
    else:
        unittest.main()
