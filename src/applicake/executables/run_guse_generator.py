#!/usr/bin/env python
'''
Created on Apr 10, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import GeneratorRunner
from applicake.applications.proteomics.openbis.generator import GuseGenerator

runner = GeneratorRunner()
application = GuseGenerator()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)