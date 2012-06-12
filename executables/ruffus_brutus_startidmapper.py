'''
Created on Jun 12, 2012

@author: quandtan
'''

import sys
from ruffus import *
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.openms.peptideproteinprocessing.idmapper import IdMapper

def idmapper():
    sys.argv = ['', '-i', 'featurefindercentroided.ini', '-o', 'idmapper'
                ]
    runner = WrapperRunner()
#    application = FeatureFinderCentroided()
    application = IdMapper()
    exit_code = runner(sys.argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed [%s]" % ('idmapper',exit_code)) 
         

pipeline_run([idmapper])