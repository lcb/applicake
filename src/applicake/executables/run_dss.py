#!/usr/bin/env python
'''
Created on Mar 28, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import BasicWrapperRunner
from applicake.applications.proteomics.openbis.dss import Dss

runner = BasicWrapperRunner()
wrapper = Dss()
exit_code = runner(sys.argv, wrapper)
print exit_code

