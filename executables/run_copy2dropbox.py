#!/usr/bin/env python
'''
Created on Jun 19, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import ApplicationRunner
from applicake.applications.proteomics.openbis.dropbox import Copy2Dropbox

runner = ApplicationRunner()
app = Copy2Dropbox()
exit_code = runner(sys.argv,app)
print exit_code