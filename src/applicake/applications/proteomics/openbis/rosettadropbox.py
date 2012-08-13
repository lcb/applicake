'''
Created on Aug 10, 2012

@author: lorenz
'''
import os
import shutil
from applicake.utils.fileutils import FileUtils
from applicake.applications.proteomics.openbis.dropbox import Copy2Dropbox
from applicake.framework.informationhandler import BasicInformationHandler

class Copy2RosettaDropbox(Copy2Dropbox):
 
    def copy_dropbox_specific_files(self,info,log,path):
        keys = ['ROSETTAMERGEDOUT']
        files = []
        for key in keys:
            if info.has_key(key):
                if isinstance(info[key], list):
                    files = info[key]
                else:
                    files = [info[key]]
                for file in files:
                    try:
                        shutil.copy(file,path)
                        log.debug('Copy [%s] to [%s]' % (file,path))
                    except:
                        if FileUtils.is_valid_file(log, file):
                            log.debug('file [%s] already exists' % file)
                        else:
                            log.fatal('Stop program because could not copy [%s] to [%s]' % (file,path))
                            return(1,info,log)
            else:
                log.error('info did not contain key [%s]' % key)
                return 1, info
        return 0,info    
    
    def main(self,info,log):
        
        exit_code, info = super(Copy2RosettaDropbox,self).main(info,log)
        
        if not info.has_key('ROSETTAMERGEDOUT'):
            log.error('Did not find mandatory key [ROSETTAMERGEDOUT]')
            return 1, info
        
        info_copy = info.copy()
        info_copy[self.OUTPUT] = os.path.join(self._get_dropboxdir(info),'dataset.properties')
        BasicInformationHandler().write_info(info_copy, log)
        
        return exit_code, info
