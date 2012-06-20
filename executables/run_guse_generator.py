#!/usr/bin/env python
'''
Created on Apr 10, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import IniFileRunner
from applicake.applications.proteomics.openbis.generator import GuseGenerator

runner = IniFileRunner()
application = GuseGenerator()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)