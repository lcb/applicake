"""
Created on Aug 10, 2012

@author: lorenz
"""

import os
import subprocess

from applicake.framework.keys import Keys
from applicake.framework.informationhandler import IniInformationHandler
from applicake.applications.proteomics.openbis.dropbox import Copy2Dropbox
from applicake.utils.dictutils import DictUtils


class Copy2SwathDropbox(Copy2Dropbox):
    """
    Copy files to an Openbis generic dropbox.
    
    """

    def main(self, info, log):
        #TODO: simplify "wholeinfo" apps
        #re-read INPUT to get access to whole info, needs set_args(INPUT). add runnerargs to set_args if modified by runner
        ini = IniInformationHandler().get_info(log, info)
        info = DictUtils.merge(log, info, ini)

        stagebox = self._make_stagebox(log, info)
        
        self._keys_to_dropbox(log, info, ['ALIGNMENT_TSV'], stagebox)
        #patch: compress align.csv, but not the matrix
        subprocess.check_call('gzip '+stagebox+'/*',shell=True)
        self._keys_to_dropbox(log, info, ['ALIGNMENT_MATRIX'], stagebox)

        #compress all mprophet files into one zip
        archive = os.path.join(stagebox, 'mprophet_files.zip')
        keys = ['MPROPHET_TSV','MPROPHET_STATS']
        for key in keys:
            if not isinstance(info[key],list):
                info[key] = [info[key]]
            subprocess.check_call('zip -j ' + archive + '  ' + " ".join(info[key]) ,shell=True)

        #compress featuretsv files into one zip
        archive = os.path.join(stagebox, 'featureTSVs.zip')
        if not isinstance(info['FEATURETSV'], list):
            info['FEATURETSV'] = [info['FEATURETSV']]
        subprocess.check_call('zip -j ' + archive + '  ' + " ".join(info['FEATURETSV']), shell=True)

        #SPACE PROJECT given
        dsinfo = {}
        dsinfo['SPACE'] = info['SPACE']
        dsinfo['PROJECT'] = info['PROJECT']
        dsinfo['PARENT_DATASETS'] = info[Keys.DATASET_CODE]
        dsinfo['DATASET_TYPE'] = 'SWATH_RESULT'
        dsinfo['EXPERIMENT_TYPE'] = 'SWATH_SEARCH'
        dsinfo['EXPERIMENT'] = self._get_experiment_code(info)
        dsinfo[Keys.OUTPUT] = os.path.join(stagebox, 'dataset.attributes')
        IniInformationHandler().write_info(dsinfo, log)

        expinfo = {}
        expinfo['PARENT-DATA-SET-CODES'] = info[Keys.DATASET_CODE]
        for key in ['COMMENT', 'TRAML', 'EXTRACTION_WINDOW', 'RT_EXTRACTION_WINDOW', 'MIN_UPPER_EDGE_DIST',
                    'MPR_NUM_XVAL', 'IRTTRAML', 'MIN_RSQ', 'WORKFLOW',
                    #'WINDOW_UNIT','MPR_MAINVARS','MPR_VARS','MPR_LDA_PATH','MIN_COVERAGE'
        ]:
            if key in info:
                expinfo[key] = info[key]
        expinfo[Keys.OUTPUT] = os.path.join(stagebox, 'experiment.properties')
        IniInformationHandler().write_info(expinfo, log)

        infocopy = info.copy()
        infocopy[Keys.OUTPUT] = os.path.join(stagebox, 'input.ini')
        IniInformationHandler().write_info(infocopy, log)

        self._move_stage_to_dropbox(stagebox, info['DROPBOX'], keepCopy=False)
        return 0, info
        
