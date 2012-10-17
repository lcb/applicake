#!/usr/bin/env python
'''
Created on Oct 17, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import ApplicationRunner
from applicake.applications.proteomics.sybit.fdr2probability import Fdr2ProbabilityPython

runner = ApplicationRunner()
application = Fdr2ProbabilityPython()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)