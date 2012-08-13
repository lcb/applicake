#!/usr/bin/env python
'''
Created on Mar 28, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.openbis.dss import Dss

runner = WrapperRunner()
application = Dss()
exit_code = runner(sys.argv, application)
print exit_code

