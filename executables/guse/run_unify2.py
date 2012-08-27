#!/usr/bin/env python
'''
Created on May 24, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import IniFileRunner2
from applicake.applications.commons.unifier2 import Unifier2

runner = IniFileRunner2()
application = Unifier2()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)