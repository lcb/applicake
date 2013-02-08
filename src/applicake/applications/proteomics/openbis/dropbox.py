'''
Created on Jun 19, 2012

@author: quandtan
'''

import os
from applicake.framework.interfaces import IApplication
from applicake.utils.fileutils import FileUtils
import shutil
from applicake.framework.informationhandler import BasicInformationHandler

class Copy2Dropbox(IApplication):
    '''
    Copy certain files to the openbis dropbox.
    '''

    def _get_dropboxdir(self, info):
        space = info['SPACE']
        project = info['PROJECT']
        prefix = ''
        if info.has_key(self.JOB_IDX):
            prefix = info[self.JOB_IDX]
        if info.has_key(self.PARAM_IDX):
            prefix = '%s.%s' % (prefix,info[self.PARAM_IDX])
        dirname = '%s+%s+%s' % (space, project, prefix)
        #return os.path.join(info['DROPBOX'],dirname)
        return os.path.join(info[self.WORKDIR],dirname)
    
    def copy_dropbox_specific_files(self,info,log,path):
        """
        Copy the dropbox-specific files into the OpenBIS dropbox.
        
        @type info: dict         
        @param info: Dictionary object with information needed by the class
        @type log: Logger 
        @param log: Logger to store log messages    
        @type path: string
        @param path: Path to the OpenBIS-dropbox   
        
        @rtype: (int,dict)
        @return: Tuple of 2 objects; the exit code and the (updated) info object.
        """
        raise NotImplementedError("copy_dropbox_specific_files() is not implemented") 

    def main(self,info,log):
        """
        See super class.
        """
        path = self._get_dropboxdir(info)
        FileUtils.makedirs_safe(log, path,clean=True)
        exit_code,info = self.copy_dropbox_specific_files(info, log, path)
        if exit_code !=0:
            return exit_code,info
        # write a copy of the  info object with the current status to the dopbox dir 
        info_copy = info.copy()
        info_copy[self.OUTPUT] = os.path.join(path,'search.properties')
        BasicInformationHandler().write_info(info_copy, log)
        
        shutil.copy(path, info['DROPBOXDIR'])
        info['DROPBOXSTAGE'] = path
        
        return exit_code,info
        
    def set_args(self,log,args_handler):
        """
        See interface
        """        
        args_handler.add_app_args(log, 'WORKDIR', 'wd')
        args_handler.add_app_args(log, 'DROPBOX', 'Path to the dropbox folder used to upload data to OpenBIS.')
        args_handler.add_app_args(log, 'SPACE', 'OpenBIS space')
        args_handler.add_app_args(log, 'PROJECT', 'Project in the OpenBIS space.')
        args_handler.add_app_args(log, self.JOB_IDX, 'Job id of the workflow')
        args_handler.add_app_args(log, self.PARAM_IDX, 'Index of the parameter set (if a sweep was performed).')       
        args_handler.add_app_args(log, self.COPY_TO_WD, 'Files which are created by this application', action='append')
#        self.PARAM_IDX,self.DATASET_CODE,self.DATASET_CODE        
        return args_handler        

class Copy2IdentDropbox(Copy2Dropbox):
    """
    Copy files to an Openbis-prot_ident_dropbox.
    
    This dropbox is specified for MS-Search experiements.
    """
        
    
    def copy_dropbox_specific_files(self,info,log,path):
        """
        See super class.
        """
        keys = ['PEPXMLS','PEPCSV','PROTXML']
        files = []
        for key in keys:
            if info.has_key(key):
                if isinstance(info[key], list):
                    files = info[key]
                else:
                    files = [info[key]]
                for file in files:
                    try:
                        # need to adapt file extension of the protxml file
                        if key == 'PROTXML':
                            basename = os.path.splitext(os.path.split(path)[1])[0]
                            new_file_path = os.path.join(path,'%s.prot.xml' % (basename))
                            log.debug('found protxml. hence copy [%s] to [%s]' % (file,new_file_path))
                            shutil.copy(file,new_file_path)
                        else:
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
        """
        See super class.
        """
        #need to rename key FDR to PEPTIDEFDR before copying it to the dropbox
        if not info.has_key('FDR'):
            log.error('Did not find mandatory key [FDR]')
            return 1, info
        log.debug('Rename key [FDR] to key [PEPTIDEFDR]')
        info['PEPTIDEFDR'] = info['FDR']
        del info['FDR']
        # need to add 'DBASENAME
        info['DBASENAME'] = os.path.splitext(os.path.split(info['DBASE'])[1])[0]
        # need to set PARENT-DATASET-CODES for lfq
        info['PARENT-DATA-SET-CODES']=info[self.DATASET_CODE]
        # set values to NONE if they were e.g. "" before
        check_keys = ['STATIC_MODS','VARIABLE_MODS']
        for key in check_keys:
            if not info.has_key(key) or info[key] == "":
                info[key] = 'NONE'
        return super(Copy2IdentDropbox,self).main(info,log)
        
 
