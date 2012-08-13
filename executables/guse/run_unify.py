#!/usr/bin/env python
'''
Created on May 24, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import IniFileRunner2
from applicake.applications.commons.inifile import Unifier

runner = IniFileRunner2()
application = Unifier()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)