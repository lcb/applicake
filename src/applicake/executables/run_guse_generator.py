#!/usr/bin/env python
'''
Created on Apr 10, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import BasicApplicationRunner
from applicake.applications.commons.generator import GuseGenerator


runner = BasicApplicationRunner()
wrapper = GuseGenerator()
exit_code = runner(sys.argv,wrapper)
print exit_code
sys.exit(exit_code)