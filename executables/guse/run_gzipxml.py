#!/usr/bin/env python
'''
Created on Dec 5, 2012

@author: lorenz
'''

import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.openswath.gzipxml import gzipXml

runner = WrapperRunner()
application = gzipXml()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)