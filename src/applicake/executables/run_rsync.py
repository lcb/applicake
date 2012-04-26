#!/usr/bin/env python

import sys
from applicake.applications.os.rsync import Rsync
from applicake.framework.runner import BasicWrapperRunner
#some like it (s)ho(r)t!
print BasicWrapperRunner().__call__(sys.argv, Rsync())
