#!/usr/bin/env python
'''
Created on Aug 30, 2012

@author: quandtan
'''
import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.openms.peptideproteinprocessing.idmapper import IdMapper

runner = WrapperRunner()
application = IdMapper()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)