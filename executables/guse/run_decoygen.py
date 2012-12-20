#!/usr/bin/env python
'''
Created on Jun 6, 2012

@author: quandtan
'''
import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.openswath.decoygen import OpenSwathDecoyGenerator

runner = WrapperRunner()
application = OpenSwathDecoyGenerator()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)