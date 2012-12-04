'''
Created on Aug 10, 2012

@author: lorenz
'''

import shutil
from applicake.utils.fileutils import FileUtils

from applicake.applications.proteomics.openbis.dropbox import Copy2Dropbox

class Copy2SwathDropbox(Copy2Dropbox):
    """
    Copy files to an Openbis-openswath_dropbox.
    
    """
        
    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, 'MPROPHET_STATS', 'mprophet stats')
        args_handler.add_app_args(log, 'COMPRESS_OUT', 'compressed featureXMLwithMprophet')
        args_handler.add_app_args(log, 'MPROPHET_TSV', 'mprophet allpeakgroups tsv soutput')
        return super(Copy2SwathDropbox, self).set_args(log,args_handler)
    
    def copy_dropbox_specific_files(self,info,log,path):
        """
        See super class.
        """
        keys = ['MPROPHET_TSV','MPROPHET_STATS','COMPRESS_OUT']
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
                            log.warn('Could not copy, file [%s] already exists' % file)
                        else:
                            log.fatal('Stop program because could not copy [%s] to [%s]' % (file,path))
                            return(1,info,log)
            else:
                log.error('info did not contain key [%s]' % key)
                return 1, info
        return 0,info    
    
   