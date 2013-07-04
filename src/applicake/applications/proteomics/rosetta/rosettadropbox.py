"""
Created on Aug 10, 2012

@author: lorenz
"""
import os
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

        stagebox = self._make_stagebox(log, info)

        self._keys_to_dropbox(log, info, 'ROSETTA_COMPRESSEDOUT', stagebox)

        dsattr = {}
        dsattr['SPACE'] = info['SPACE']
        dsattr['PROJECT'] = info['PROJECT']
        dsattr['EXPERIMENT'] = info['EXPERIMENT']
        dsattr['DATASET_TYPE'] = 'ROSETTA_OUTFILE'
        dsattr[Keys.OUTPUT] = os.path.join(stagebox, 'dataset.attributes')
        IniInformationHandler().write_info(dsattr, log)
        
        dsprop = info.copy()
        dsprop[Keys.OUTPUT] = os.path.join(stagebox, 'dataset.properties')
        IniInformationHandler().write_info(dsprop, log)

        self._move_stage_to_dropbox(stagebox, info['DROPBOX'], keepCopy=False)

        return 0, info
