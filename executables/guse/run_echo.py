#!/usr/bin/env python
'''
Created on Mar 28, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.os.echo import Echo

runner = WrapperRunner()
application = Echo()
exit_code = runner(sys.argv,application)
print exit_code


 
