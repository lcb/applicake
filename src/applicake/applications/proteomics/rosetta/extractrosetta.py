'''
Created on Jul 11, 2012

@author: loblum
'''

from applicake.framework.interfaces import IWrapper

class Extractrosetta(IWrapper):
    '''
    Extract rosetta dataset tgz to flat folder WORKDIR
    '''
    _default_prefix = 'pax'
    
    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def prepare_run(self,info,log):
        """
        """
        prefix,info = self.get_prefix(info,log)        
        wd = info[self.WORKDIR]
        info['ROSETTAINPUTDIR'] = wd
        wdescaped = wd.replace('/','\/') + '\/'
        archivepath = None
        for dssout in info[self.DSSOUTPUT]:
            if dssout.endswith('tgz'):
                archivepath = dssout  
        #prefix = pax command, archivepath = dataset/tgz path, wdescaped = WORKDIR in a way pax needs it
        #the -s replaces all tgz subdirs by the WORKDIR, so all files land in the same folder  
        command = '%s -rzf %s -s "/.*\//%s/"' % (prefix,archivepath,wdescaped)
        return command,info

    def set_args(self,log,args_handler):
        """
        See super class.
        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.DSSOUTPUT, 'Dssout to know which tgz to use')
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        """ 
        return run_code,info
