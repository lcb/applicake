#!/usr/bin/env python
'''
Created on Jun 6, 2012

@author: quandtan
'''
import sys
from applicake.framework.runner import ApplicationRunner
from applicake.applications.proteomics.openswath.copytraml import CopyTraml

runner = ApplicationRunner()
application = CopyTraml()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)