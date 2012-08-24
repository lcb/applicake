#!/usr/bin/env python
'''
Created on Apr 10, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import IniFileRunner2
from applicake.applications.commons.generator import ParametersetGenerator

runner = IniFileRunner2()
application = ParametersetGenerator()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)