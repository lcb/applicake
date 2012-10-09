#!/usr/bin/env python
'''
Created on Mar 28, 2012

@author: johant
'''

import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.srm.anubis import Anubis

runner = WrapperRunner()
application = Anubis()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)
