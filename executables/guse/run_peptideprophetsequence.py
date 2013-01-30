#!/usr/bin/env python
'''
Created on Jun 19, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.tpp.peptideprophetsequence import PeptideProphetSequence

runner = WrapperRunner()
application = PeptideProphetSequence()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)