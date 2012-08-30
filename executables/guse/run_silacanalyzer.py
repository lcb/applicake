#!/usr/bin/env python
'''
Created on Aug 30, 2012

@author: quandtan
'''
import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.openms.quantification.silacanalyzer import SilacAnalyzer

runner = WrapperRunner()
application = SilacAnalyzer()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)