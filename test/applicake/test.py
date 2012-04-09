'''
Created on Apr 9, 2012

@author: quandtan
'''
from applicake.framework.runner import ApplicationInformation

info = ApplicationInformation()
info.BASEDIR = '/tmp'
info.set_jobid()
print info.JOB_IDX
info.TESTME = ['test','andreas']
for key in info.keys():
    if 