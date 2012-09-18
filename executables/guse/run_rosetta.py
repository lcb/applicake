#!/usr/bin/env python
'''
Created on Mar 28, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.rosetta.rosetta import Rosetta

runner = WrapperRunner()
application = Rosetta()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)

 
