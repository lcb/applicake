'''
Created on Apr 29, 2012

@author: quandtan
'''
import sys
from ruffus import *
from applicake.framework.runner import WrapperRunner
from applicake.applications.proteomics.openms.filehandling.fileconverter import Mzxml2Mzml

def mzxml2mzml():
    args = 'bla.py --BASEDIR /tmp --STORAGE file --TEMPLATE template.ini --PREFIX FileConverter --MZXML /tmp/ALBU_HUMAN_0F_CAM_core.mzXML --MZML ALBU_HUMAN_0F_CAM_core.mzML' # /Applications/OpenMS-1.9.0/TOPP/
    sys.argv = args.split(' ')
    runner = WrapperRunner()
    application = Mzxml2Mzml()
    exit_code = runner(sys.argv,application)
    print exit_code
    if exit_code != 0:
        raise Exception("mzxml2mzml failed with exit code [%s]" % exit_code)    
    
    
@follows(mzxml2mzml)
def task_2():
    print 'world'
    
pipeline_run([task_2])