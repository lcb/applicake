#!/usr/bin/env python
'''
Created on Jun 19, 2012

@author: quandtan
'''

import sys
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.sybit.protxml2modifications import ProtXml2Modifications

runner = WrapperRunner()
application = ProtXml2Modifications()
exit_code = runner(sys.argv,application)
print exit_code
sys.exit(exit_code)