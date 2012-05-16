'''
Created on Apr 29, 2012

@author: quandtan
'''
import sys
from ruffus import *
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.openms.filehandling.fileconverter import Mzxml2Mzml

def mzxml2mzml():
    args = 'test.py --BASEDIR /tmp --STORAGE file --TEMPLATE template.ini --PREFIX /Applications/OpenMS-1.9.0/TOPP/FileConverter'
    sys.argv = args.split(' ')
    runner = WrapperRunner()
    application = Mzxml2Mzml()
    exit_code = runner(sys.argv,application)
    print exit_code    
    
    
@follows(mzxml2mzml)
def task_2():
    print 'world'
    
pipeline_run([task_2])