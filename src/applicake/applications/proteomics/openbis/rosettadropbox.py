'''
Created on Aug 10, 2012

@author: lorenz
'''
import os
from applicake.applications.proteomics.openbis.dropbox import Copy2Dropbox
from applicake.framework.informationhandler import BasicInformationHandler

class Copy2RosettaDropbox(Copy2Dropbox):
    
    def main(self,info,log):
        info['DROPBOXSTAGE'] = self._make_stagebox(log, info)
 
        keys = ['ROSETTA_FLAGSFILE','ROSETTA_COMPRESSEDOUT']
        self._keys_to_dropbox(log, info, keys, info['DROPBOXSTAGE'])
        
        info_copy = info.copy()
        info_copy[self.OUTPUT] = os.path.join(info['DROPBOXSTAGE'],'dataset.properties')
        BasicInformationHandler().write_info(info_copy, log)
        
        attrs = {}
        attrs['DATASET_TYPE'] = 'ROSETTA_OUTFILE'
        attrs['SPACE'] = info['SPACE']
        attrs['PROJECT'] = info['PROJECT'] 
        attrs['EXPERIMENT'] = info['EXPERIMENT']
        attrs['PARENT_DATASETS']= info['DATASET_CODE']
        attrs[self.OUTPUT] = os.path.join(info['DROPBOXSTAGE'],'dataset.attributes')
        BasicInformationHandler().write_info(attrs, log)
        
        self._move_stage_to_dropbox(info['DROPBOXSTAGE'], info['DROPBOX'], keepCopy=False)
        return 0, info
