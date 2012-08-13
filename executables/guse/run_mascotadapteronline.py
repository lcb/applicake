#!/usr/bin/env python
'''
Created on Jun 24, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.openms.identification.macotadapteronline import MascotAdapterOnline

runner = WrapperRunner()
application = MascotAdapterOnline()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)