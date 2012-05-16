'''
Created on Apr 29, 2012

@author: quandtan
'''
import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.openms.filehandling.fileconverter import Mzxml2Mzml

runner = WrapperRunner()
application = Mzxml2Mzml()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)