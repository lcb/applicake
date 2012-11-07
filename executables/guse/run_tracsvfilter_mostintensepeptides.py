'''
Created on Nov 6, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import ApplicationRunner
from applicake.applications.proteomics.srm.tracsvfilter import *

runner = ApplicationRunner()
application = SelectMostIntensePeptides()
exit_code = runner(sys.argv,application)
print exit_code

sys.exit(exit_code)