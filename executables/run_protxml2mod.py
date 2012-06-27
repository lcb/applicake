#!/usr/bin/env python
'''
Created on Jun 19, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import ApplicationRunner
from applicake.applications.proteomics.sybit.protxml2modifications import ProtXml2Modifications

runner = ApplicationRunner()
application = ProtXml2Modifications()
exit_code = runner(sys.argv,application)
print exit_code