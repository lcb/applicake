#!/usr/bin/env python

import sys
from applicake.applications.os.rsync import Rsync
from applicake.framework.runner import WrapperRunner
#some like it (s)ho(r)t!
print WrapperRunner().__call__(sys.argv, Rsync())
