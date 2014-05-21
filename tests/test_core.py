import unittest
import sys
import os
import tempfile
import shutil
import logging
from StringIO import StringIO

from appliapps.examples.b_extecho import ExternalEcho


class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tdir = tempfile.mkdtemp(dir=".")
        os.chdir(cls.tdir)
        with open("input.ini", "w") as f:
            f.write("COMMENT = infofile comment")


    def test1_arg_priority(self):
        sys.stdout = StringIO()
        #should write default comment to logfile
        sys.argv = []
        ExternalEcho.main()
        assert "default comment" in sys.stdout.getvalue()

        #should write infofile comment (because higher prio than default comment) to logfile
        sys.stdout.truncate(0)
        sys.argv = ["--LOG_STORAGE", "file", "--INPUT", 'input.ini']
        ExternalEcho.main()
        assert "infofile comment" in sys.stdout.getvalue()

        #should write cmdline comment to logfile (because cmdline > infofile > default)
        sys.stdout.truncate(0)
        sys.argv = ["--LOG_STORAGE", "file", "--INPUT", 'input.ini', '--COMMENT', 'cmdline comment']
        ExternalEcho.main()
        assert "cmdline comment" in sys.stdout.getvalue()
        sys.stdout = sys.__stdout__

    @classmethod
    def tearDownClass(cls):
        os.chdir("..")
        shutil.rmtree(cls.tdir)
