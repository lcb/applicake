#!/usr/bin/env python
'''
Created on Dec 11, 2012

@author: loblum
'''
import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.spectrast.spectrast2tsv2traml import Spectrast2TSV2traML 

runner = WrapperRunner()
application = Spectrast2TSV2traML()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)