#!/usr/bin/env python
'''
Created on Apr 29, 2012

@author: quandtan
'''
import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.openms.filehandling.idfileconverter import IdXml2PepXml

runner = WrapperRunner()
application = IdXml2PepXml()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)