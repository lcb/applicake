#!/usr/bin/env python
'''
Created on Jul 6, 2012

@author: loblum
'''

import sys
from applicake.framework.runner import ApplicationRunner
from applicake.applications.proteomics.openbis.processexperiment import ProcessExperiment

runner = ApplicationRunner()
application = ProcessExperiment()
exit_code = runner(sys.argv,application)
print exit_code