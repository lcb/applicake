#!/usr/bin/env python
'''
Created on Jun 6, 2012

@author: quandtan
'''
import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.tpp.interactparser import InteractParser


runner = WrapperRunner()
application = InteractParser()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)