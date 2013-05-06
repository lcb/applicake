'''
Created on Aug 10, 2012

@author: lorenz
'''

import os
import subprocess

from applicake.framework.informationhandler import BasicInformationHandler
from applicake.applications.proteomics.openbis.dropbox import Copy2Dropbox

class Copy2SwathDropbox(Copy2Dropbox):
    """
    Copy files to an Openbis generic dropbox.
    
    """ 
    def main(self,info,log):  
        stagebox = self._make_stagebox(log, info) 
        
        keys = ['MPROPHET_TSV','ALIGNMENT_TSV','MPROPHET_STATS']
        self._keys_to_dropbox(log, info, keys, stagebox)
        
        #compress CSV files        
        archive = os.path.join(stagebox, 'featureTSVs.zip')
        subprocess.check_call('zip -j ' + archive + '  ' + " ".join(info['FEATURETSV']) ,shell=True)
        
        #SPACE PROJECT given
        dsinfo = {}
        dsinfo['SPACE'] = info['SPACE']
        dsinfo['PROJECT'] = info['PROJECT']
        dsinfo['PARENT_DATASETS']= info[self.DATASET_CODE]
        dsinfo['DATASET_TYPE'] = 'SWATH_RESULT'
        dsinfo['EXPERIMENT_TYPE'] = 'SWATH_SEARCH'
        dsinfo['EXPERIMENT'] = self._get_experiment_code(info)
        dsinfo[self.OUTPUT] = os.path.join(stagebox,'dataset.attributes')
        BasicInformationHandler().write_info(dsinfo, log)
        
        expinfo = {}
        expinfo['PARENT-DATA-SET-CODES'] = info[self.DATASET_CODE]
        for key in ['COMMENT','TRAML','EXTRACTION_WINDOW','RT_EXTRACTION_WINDOW','MIN_UPPER_EDGE_DIST','MPR_NUM_XVAL','IRTTRAML','MIN_RSQ','RUNDENOISER',
                    #'WINDOW_UNIT','MPR_MAINVARS','MPR_VARS','MPR_LDA_PATH','MIN_COVERAGE','WIDTH','RTWIDTH'
                   ]:
            if key in info:
                expinfo[key] = info[key]
        expinfo[self.OUTPUT] = os.path.join(stagebox,'experiment.properties')
        BasicInformationHandler().write_info(expinfo, log)
        
        infocopy = info.copy()
        infocopy[self.OUTPUT] = os.path.join(stagebox,'input.ini')
        BasicInformationHandler().write_info(infocopy, log)
        
        
        self._move_stage_to_dropbox(stagebox, info['DROPBOX'],keepCopy=False)
        return 0,info
        