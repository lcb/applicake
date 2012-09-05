#!/usr/bin/env python
'''
Created on Apr 23, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import IniFileRunner2
from applicake.applications.commons.enginecollector import GuseEngineCollector

runner = IniFileRunner2()
application = GuseEngineCollector()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)