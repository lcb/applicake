#!/usr/bin/env python
'''
Created on Apr 23, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import ApplicationRunner
from applicake.applications.commons.generator import PgradeGenerator


runner = ApplicationRunner()
application = PgradeGenerator()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)