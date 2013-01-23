#!/usr/bin/env python
'''
Created on Apr 23, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import IniFileRunner
from applicake.applications.commons.enginecollector import GuseEngineCollector

runner = IniFileRunner()
application = GuseEngineCollector()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)