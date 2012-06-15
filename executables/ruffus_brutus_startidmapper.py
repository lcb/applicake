#!/usr/bin/env python
'''
Created on Jun 12, 2012

@author: quandtan
'''

import sys
from ruffus import *
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.openms.peptideproteinprocessing.idmapper import IdMapper
from applicake.applications.proteomics.openms.peptideproteinprocessing.idconflictresolver import IdConflictResolver


def setup():
    print 'start...'

@follows(setup)
def idmapper():
    sys.argv = ['', '-i', 'featurefindercentroided.ini', '-o', 'idmapper.ini'
                ]
    runner = WrapperRunner()
    application = IdMapper()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('idmapper',exit_code)) 

@follows(idmapper)
def idconflictresolver():
    sys.argv = ['', '-i', 'idmapper.ini', '-o', 'idconflictresolver.ini'
                ]
    runner = WrapperRunner()
    application = IdConflictResolver()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('idconflictresolver',exit_code))          

pipeline_run([idconflictresolver])