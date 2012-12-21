#!/usr/bin/env python
'''
Created on Dec 11, 2012

@author: loblum
'''
import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.spectrast.spectrastirtcalibrator import SpectrastIrtCalibrator 

runner = WrapperRunner()
application = SpectrastIrtCalibrator()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)