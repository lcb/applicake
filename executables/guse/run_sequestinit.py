#!/usr/bin/env python
'''
Created on Apr 10, 2012

@author: loblum
'''

import sys
from applicake.framework.runner import IniFileRunner
from applicake.applications.proteomics.sequest.initiator import SequestInitiator

runner = IniFileRunner()
application = SequestInitiator()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)