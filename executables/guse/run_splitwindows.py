#!/usr/bin/env python
'''
Created on Nov 16, 2012

@author: loblum
'''
import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.openswath.splitwindows import SplitWindowsConvertZip

runner = WrapperRunner()
application = SplitWindowsConvertZip()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)