'''
Created on Nov 1, 2012

@author: quandtan
'''

import os
from applicake.framework.interfaces import IWrapper

class SpectrastIrtCalibrator(IWrapper):
    '''
    Wrapper for spectrast2spectrast_irt.py
    '''

    _default_prefix = 'spectrast2spectrast_irt.py'
    
    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def prepare_run(self,info,log):
        """
        See interface.

        - Define path to result file (depending on work directory)
        - If a template is used, the template is read variables from the info object are used to set concretes.
        - If there is a result file, it is added with a specific key to the info object.
        """
        
        self._result_file = os.path.join(info[self.WORKDIR],'RawRTcalib.splib')
        input_splib = info[self.SPLIB]
        info[self.SPLIB] = self._result_file
        
        prefix,info = self.get_prefix(info,log)
        options = ''
        if 'RTKIT' in info and not info['RTKIT'] == "":
            options += " -k " + info['RTKIT'].replace(";",",")
        if 'APPLYCHAUVENET' in info and info['APPLYCHAUVENET'] == "True" :
            options += " --applychauvenet"
        if 'PRECURSORLEVEL' in info and info['PRECURSORLEVEL'] == "True":
            options += " --precursorlevel"
        if 'SPECTRALEVEL' in info and info['SPECTRALEVEL'] == "True":
            options += " --spectralevel"
        
        command = '%s -i %s -o %s --rsq_threshold %s %s' % (prefix,input_splib,info[self.SPLIB],info[self.RSQ_THRESHOLD],options)
        return command,info

    def set_args(self,log,args_handler):
        """
        See super class.
        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, self.TEMPLATE, 'Path to the template file')
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory')
          
        args_handler.add_app_args(log, self.SPLIB, 'Input spectrast library in .splib format')
        args_handler.add_app_args(log, self.RSQ_THRESHOLD, 'specify r-squared threshold to accept linear regression')
        args_handler.add_app_args(log, 'RTKIT', 'RT kit')
        args_handler.add_app_args(log, 'APPLYCAUVENET', 'should Chavenets criterion be used to exclude outliers?')   
        args_handler.add_app_args(log, 'PRECURSORLEVEL', 'should precursors instead of peptides be used for grouping?')   
        args_handler.add_app_args(log, 'SPECTRALEVEL', 'do not merge or group any peptides or precursors (use raw spectra)')   
        
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        """
        if 0 != run_code:
            return run_code,info
    #out_stream.seek(0)
    #err_stream.seek(0)
        return 0,info
