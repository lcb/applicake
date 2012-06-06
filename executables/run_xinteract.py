#!/usr/bin/env python
'''
Created on Jun 6, 2012

@author: quandtan
'''
import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.tpp.xinteract import Xinteract


runner = WrapperRunner()
app = Xinteract()
exit_code = runner(sys.argv,app)
print exit_code
sys.exit(exit_code)