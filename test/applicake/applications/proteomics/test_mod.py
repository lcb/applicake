#!/usr/bin/env python2.7

import unittest
import sys

from applicake.applications.proteomics.tpp.searchengines.modifications import modstr_to_engine


class Test(unittest.TestCase):
    def test_mod(self):
        print modstr_to_engine("Carbamidomethyl (C)", "442/442.5 (STY)", "XTandem")


if __name__ == "__main__":
    if len(sys.argv) > 1 and 'test' not in sys.argv[1]:
        print sys.argv[1]
        try:
            print modstr_to_engine(sys.argv[1], "", "XTandem")
            print "OK"
        except Exception, e:
            print "ERROR"
            print e.message
    else:
        unittest.main()
