#!/usr/bin/env python
'''
Created on Mar 28, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.rosetta.extractrosetta import Extractrosetta

runner = WrapperRunner()
application = Extractrosetta()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)


 
