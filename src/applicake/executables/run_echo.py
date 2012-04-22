'''
Created on Mar 28, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import BasicWrapperRunner
from applicake.applications.os.echo import Echo


runner = BasicWrapperRunner()
wrapper = Echo()
exit_code = runner(sys.argv,wrapper)
print exit_code
sys.exit(exit_code)

 
