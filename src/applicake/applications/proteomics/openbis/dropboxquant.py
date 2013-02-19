'''
Created on Aug 10, 2012

@author: lorenz
'''

import shutil
import os
import time
from applicake.utils.fileutils import FileUtils
from applicake.framework.informationhandler import BasicInformationHandler
from applicake.framework.interfaces import IApplication

class Copy2DropboxQuant(IApplication):
    """
    Copy files to an Openbis-openswath_dropbox.
    
    """
    def _get_dropboxdir(self, info):
        space = info['SPACE']
        project = info['PROJECT']
        prefix = ''
        if info.has_key(self.JOB_IDX):
            prefix = info[self.JOB_IDX]
        if info.has_key(self.PARAM_IDX):
            prefix = '%s.%s' % (prefix,info[self.PARAM_IDX])
        if info.has_key(self.FILE_IDX):
            prefix = '%s.%s' % (prefix,info[self.FILE_IDX])
        dirname = '%s+%s+%s' % (space, project, prefix)
        return os.path.join(info['DROPBOX'],dirname)
            
    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, 'PROTXML', 'mprophet stats')
        args_handler.add_app_args(log, 'PEPCSV', 'compressed featureXMLwithMprophet')
        args_handler.add_app_args(log, 'PROTCSV', 'mprophet allpeakgroups tsv soutput')
        args_handler.add_app_args(log, 'FEATUREXMLS', 'featuretsv')
        
        args_handler.add_app_args(log, 'WORKDIR', 'wd')
        args_handler.add_app_args(log, 'DROPBOX', 'Path to the dropbox folder used to upload data to OpenBIS.')
        args_handler.add_app_args(log, 'SPACE', 'OpenBIS space')
        args_handler.add_app_args(log, 'PROJECT', 'Project in the OpenBIS space.')
        args_handler.add_app_args(log, self.JOB_IDX, 'Job id of the workflow')
        args_handler.add_app_args(log, self.PARAM_IDX, 'Index of the parameter set (if a sweep was performed).')       
        args_handler.add_app_args(log, self.COPY_TO_WD, 'Files which are created by this application', action='append')
        
        return args_handler
    
    def main(self,info,log):
        
        path = self._get_dropboxdir(info)
        FileUtils.makedirs_safe(log, path,clean=True)
        
        keys = ['PROTXML','PEPCSV','PROTCSV','FEATUREXMLS']
        files = []
        for key in keys:
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
        
        expinfo = {}
        expinfo['PARENT-DATA-SET-CODES'] = info[self.DATASET_CODE]
        expinfo['BASE_EXPERIMENT'] = info['EXPERIMENT']
        expinfo['QUANTIFICATION_TYPE'] = 'LABEL-FREE'
        expinfo['PEAKPICKER'] = 'YES'
        expinfo['MAPALIGNER'] = 'YES'
        for key in ['COMMENT','PEPXML_FDR']:
            if key in info:
                expinfo[key] = info[key]
        expinfo[self.OUTPUT] = os.path.join(path,'quantification.properties')
        BasicInformationHandler().write_info(expinfo, log)
        
        return 0,info
        