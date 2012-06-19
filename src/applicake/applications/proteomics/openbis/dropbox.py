'''
Created on Jun 19, 2012

@author: quandtan
'''

from applicake.framework.interfaces import IApplication

class Copy2Dropbox(IApplication):
    '''
    Copy certain files to the openbis dropbox.
    '''


    def _set_wd(self, info):
        space = info['SPACE']
        project = info['PROJECT']
        prefix = ''
        if info.has_key('JOBID'):
            prefix = info['JOBID']
        if info.has_key('PARAM_IDX'):
            prefix = '%s.%s' (prefix,info['PARAM_IDX'])
        info[self.WORKDIR] = '%s+%s+%s' % (space, project, prefix)
        return info

    def main(self,info,log):
        info = self._set_wd(info)
        
        keys = ['PEPXMLS','PEPCSV','PROTXML']
        files = []
        for key in keys:
            if info.has_key(key):
                if isinstance(info[key], list):
                    files = info[key]
                else:
                    files = [info[key]]
                for file in files:
                    info[self.COPY_TO_WD].append(file)
                
            else:
                log.error('info did not contain key [%s]' % key)
                return 1, info
        return 
        
    def set_args(self,log,args_handler):
        """
        See interface
        """        
        args_handler.add_app_args(log, 'DROPBOX', 'Path to the dropbox folder used to upload data to OpenBIS.')
        args_handler.add_app_args(log, 'SPACE', 'OpenBIS space')
        args_handler.add_app_args(log, 'PROJECT', 'Project in the OpenBIS space.')
        args_handler.add_app_args(log, 'JOBIDX', 'Job id of the workflow')
        args_handler.add_app_args(log, 'PARAMIDX', 'Index of the parameter set (if a sweep was performed).')
        args_handler.add_app_args(log, self.COPY_TO_WD, 'Files which are created by this application', action='append')
#        self.PARAM_IDX,self.DATASET_CODE,self.DATASET_CODE        
        return args_handler        
           