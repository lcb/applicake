'''
Created on Aug 10, 2012

@author: lorenz
'''
import shutil
from applicake.utils.fileutils import FileUtils
from applicake.applications.proteomics.openbis.dropbox import Copy2Dropbox

class Copy2RosettaDropbox(Copy2Dropbox):
    
    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, 'ROSETTAMERGEDOUT', 'Merget output.dat file')     
        return super(Copy2RosettaDropbox,self).set_args(log,args_handler)
    
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
        if not info.has_key('ROSETTAMERGEDOUT'):
            log.error('Did not find mandatory key [ROSETTAMERGEDOUT]')
            return 1, info
        
        return super(Copy2RosettaDropbox,self).main(info,log)
