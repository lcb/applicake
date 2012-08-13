#!/usr/bin/env python
'''
Created on May 24, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.sybit.fdr2probability import Fdr2Probability

runner = WrapperRunner()
application = Fdr2Probability()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)