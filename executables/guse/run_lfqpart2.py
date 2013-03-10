#!/usr/bin/env python
'''
Created on Apr 29, 2012

@author: quandtan
'''
import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.openms.quantification.lfqpart1 import LFQpart2


runner = WrapperRunner()
application = LFQpart2()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)