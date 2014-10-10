#!/usr/bin/env python
import os
import sys
import subprocess

from ruffus import *


basepath = os.path.dirname(__file__) + '/../../'


def setup():
    if len(sys.argv) > 1 and sys.argv[1] == 'cont':
        print 'Continuing with existing input.ini (Ruffus should skip to the right place automatically)'
    else:
        print 'Starting from scratch by creating new input.ini'
        subprocess.call("rm *ini* *.log", shell=True)
        with open("input.ini", 'w+') as f:
            f.write("COMMENT = hello,world")


@follows(setup)
@split("input.ini", "split.ini_*")
def split(infile, unused_outfile):
    subprocess.check_call(['python', basepath + 'appliapps/flow/split.py',
                           '--INPUT', infile, '--SPLIT', 'split.ini', '--SPLIT_KEY', 'COMMENT'])


@transform(split, regex("split.ini_"), "echo.ini_")
def echo(infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/examples/a_pyecho.py',
                           '--INPUT', infile, '--OUTPUT', outfile])


@merge(echo, "merged.ini")
def merge(unused_infile, outfile):
    subprocess.check_call(['python', basepath + 'appliapps/flow/merge.py',
                           '--MERGE', 'echo.ini', '--MERGED', outfile])


if __name__ == "__main__":
    print "STARTING RUFFUS PIPELINE"
    pipeline_run([merge], multiprocess=2)
    print "IN CASE YOU SEE THIS WORKFLOW FINISHED SUCESSFULLY"