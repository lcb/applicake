
import os,shutil

from applicake.framework.informationhandler import BasicInformationHandler
from applicake.applications.proteomics.openbis.dropbox import Copy2Dropbox

class Copy2SequestDropbox(Copy2Dropbox):
    
    def main(self,info,log):
        """
        See super class.
        """
        info['DROPBOXSTAGE'] = self._make_stagebox(log, info)
        
        keys = ['PEPXMLS','PEPCSV']
        self._keys_to_dropbox(log, info, keys, info['DROPBOXSTAGE'])
        
        #protxml special naming
        filename = os.path.basename(info['DROPBOXSTAGE']) + '.prot.xml'
        filepath = os.path.join(info['DROPBOXSTAGE'],filename)
        shutil.copy(info['PROTXML'],filepath)
        
        #search.properties requires some specific fields
        info['PEPTIDEFDR'] = info['FDR']
        info['DBASENAME'] = os.path.splitext(os.path.split(info['DBASE'])[1])[0]
        info['PARENT-DATA-SET-CODES']=info[self.DATASET_CODE]
        
        # set values to NONE if they were e.g. "" before
        #check_keys = ['STATIC_MODS','VARIABLE_MODS']
        #for key in check_keys:
        #    if not info.has_key(key) or info[key] == "":
        #        info[key] = 'NONE'
        
        sinfo = info.copy()
        sinfo[self.OUTPUT] = os.path.join(info['DROPBOXSTAGE'],'search.properties')
        BasicInformationHandler().write_info(sinfo, log)
        
        info['DROPBOXSTAGE'] = self._move_stage_to_dropbox(info['DROPBOXSTAGE'], info['DROPBOX'],keepCopy=True)
        
        return 0,info