#!/usr/bin/env python
'''
Created on Sep 4, 2012

@author: quandtan
'''
import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.openms.peptideproteinprocessing.falsediscoveryrate import FalseDiscoveryRate

runner = WrapperRunner()
application = FalseDiscoveryRate()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)