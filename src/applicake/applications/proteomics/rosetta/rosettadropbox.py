"""
Created on Aug 10, 2012

@author: lorenz
"""
import os
import socket
from applicake.framework.keys import Keys
from applicake.applications.proteomics.openbis.dropbox import Copy2Dropbox
from applicake.framework.informationhandler import IniInformationHandler
from applicake.utils.dictutils import DictUtils


class Copy2RosettaDropbox(Copy2Dropbox):
    def main(self, info, log):
        #TODO: simplify "wholeinfo" apps
        #re-read INPUT to get access to whole info, needs set_args(INPUT). add runnerargs to set_args if modified by runner
        ini = IniInformationHandler().get_info(log, info)
        info = DictUtils.merge(log, info, ini)

        info['WORKFLOW'] = self._extendWorkflowID(info['WORKFLOW'])
        stagebox = self._make_stagebox(log, info)

        self._keys_to_dropbox(log, info, 'ROSETTA_COMPRESSEDOUT', stagebox)

        dsattr = {}
        dsattr['SPACE'] = info['SPACE']
        dsattr['PROJECT'] = info['PROJECT']
        dsattr['EXPERIMENT'] = info['OUTEXPERIMENT']
        dsattr['DATASET_TYPE'] = 'ROSETTA_OUTFILE'
        dsattr[Keys.OUTPUT] = os.path.join(stagebox, 'dataset.attributes')
        IniInformationHandler().write_info(dsattr, log)
        
        dsprop = {}
        #N_MODELS missing
        for key in ['SEQ', 'COMMENT', 'ROSETTA_VERSION', 'RUN__PROTOCOL', 'RUN__SHUFFLE', 'INFRASTRUCTURE', 'N_MODELS', 
                    'DATABASE', 'IN__FILE__ALIGNMENT', 'CM__ALN_FORMAT', 'FRAG3', 'FRAG9', 'IN__FILE__FASTA', 'IN__FILE__FULLATOM', 
                    'IN__FILE__PSIPRED_SS2', 'IN__DETECT_DISULF', 'IN__FILE__TEMPLATE_PDB', 'LOOPS__FRAG_SIZES', 'LOOPS__FRAG_FILES', 
                    'IDEALIZE_AFTER_LOOP_CLOSE', 'LOOPS__EXTENDED', 'LOOPS__BUILD_INITIAL', 'LOOPS__REMODEL', 'LOOPS__RELAX', 
                    'RANDOM_GROW_LOOPS_BY', 'SELECT_BEST_LOOP_FROM', 'RELAX__FAST', 'RELAX__DEFAULT_REPEATS', 'SILENT_DECOYTIME', 
                    'FAIL_ON_BAD_HBOND', 'BGDT', 'EVALUATION__GDTMM', 'OUT__FILE__SILENT_STRUCT_TYPE']:
            dsprop[key]=info[key]

        dsprop[Keys.OUTPUT] = os.path.join(stagebox, 'dataset.properties')
        IniInformationHandler().write_info(dsprop, log)

        self._move_stage_to_dropbox(stagebox, info['DROPBOX'], keepCopy=False)

        return 0, info
