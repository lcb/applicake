#!/usr/bin/env python2.7

import unittest
import sys

from applicake.applications.proteomics.tpp.searchengines.modifications import modstr_to_engine


class Test(unittest.TestCase):
    def test_mod(self):
        print modstr_to_engine("Carbamidomethyl (C)", "442/442.5 (STY)", "XTandem")


if __name__ == "__main__":
    if len(sys.argv) > 1 and 'test' not in sys.argv[1]:
        mod = sys.argv[1]
        print "Testing modification '%s'" % mod
        try:
            for i in ['XTandem', 'Omssa', 'Myrimatch', 'Comet']:
                modstr_to_engine(mod, "", i)
                modstr_to_engine("", mod, i)
            #print out one example to show masses. myri varmod is most compact
            _, p, _ = modstr_to_engine("", mod, 'Myrimatch')
            print p
            print "OK"
        except Exception, e:
            print "ERROR"
            print e.message
    else:
        unittest.main()
