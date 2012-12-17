#!/usr/bin/env python
'''
Created on Apr 29, 2012

@author: quandtan
'''
import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.tpp.mzxml2search import Mzxml2Search

runner = WrapperRunner()
application = Mzxml2Search()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)