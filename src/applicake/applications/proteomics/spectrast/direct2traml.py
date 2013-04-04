#!/usr/bin/env python
'''
Created on Mar 28, 2012

@author: loblum
'''

import os
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator

class Direct2TraML(IWrapper):
    """
    Wrapper for the famous spectrast2traml.sh script
    """
    def prepare_run(self,info,log):

        consensuslib = os.path.join(info[self.WORKDIR],'consensuslib')
        if not os.access(os.path.dirname(info['LIBOUTBASE']), os.W_OK):
            log.warn("The folder [%s] is not writable, falling to workflow folder [%s]!" %(info['LIBOUTBASE'],info[self.WORKDIR]))
            info['LIBOUTBASE'] = os.path.join(info[self.WORKDIR], os.path.basename(info['LIBOUTBASE']))
        self._result_file = info[self.TRAML] = info['LIBOUTBASE'] + '_' + info[self.PARAM_IDX] +  '.TraML'
        
        command = 'spectrast -cAC -c_BIN! -cN%s %s && direct2traml.sh %s %s %s' % (consensuslib, 
                                                                                   info[self.SPLIB],
                                                                                   consensuslib+'.splib',
                                                                                   info[self.TRAML],
                                                                                   self.set_opts(info))
        return command,info
    
    def set_opts(self,info):
        tsvopts = '-k openswath '
        tsvopts += ' --limits ' + info['TSV_MASS_LIMITS'].replace("-",",")
        tsvopts += ' --min %s --max %s ' % info['TSV_ION_LIMITS'].split("-")
        tsvopts += ' --precision ' + info['TSV_PRECISION']
        if info.has_key('TSV_REMOVE_DUPLICATES') and info['TSV_REMOVE_DUPLICATES'] == "True":
            tsvopts += ' --remove-duplicates'
        if info.has_key('TSV_EXACT') and info['TSV_EXACT'] == "True":
            tsvopts += ' --exact'
        if info.has_key('TSV_GAIN') and info['TSV_GAIN'] != "":
            tsvopts += ' --gain '+info['TSV_GAIN'].replace(";",",")
        if info.has_key('TSV_CHARGE') and info['TSV_CHARGE'] != "":
            tsvopts += ' --charge '+info['TSV_CHARGE']
        if info.has_key('TSV_SERIES') and info['TSV_SERIES'] == "":
            tsvopts += ' --series '+info['TSV_SERIES']
        
        decoyopts = '-append -exclude_similar ' 
        decoyopts += '-method ' + info['SWDECOY_METHOD']
        if info.has_key('SWDECOY_THEORETICAL') and info['SWDECOY_THEORETICAL'] == "True":
            decoyopts += ' -theoretical'
        
        return '\''+tsvopts+'\' \''+decoyopts+'\''
    
    def set_args(self,log,args_handler):
        """
        See interface
        """        
        args_handler.add_app_args(log, self.SPLIB, 'Spectrast library in .splib format')
        args_handler.add_app_args(log, self.WORKDIR, 'workdir')
        
        args_handler.add_app_args(log, 'LIBOUTBASE', 'Folder to put output libraries')
        args_handler.add_app_args(log, self.PARAM_IDX, 'Parameter index to distinguish')   
        
        args_handler.add_app_args(log, 'SWDECOY_METHOD', 'decoy generation method (shuffle, pseudo-reverse, reverse, shift)')
        args_handler.add_app_args(log, 'SWDECOY_THEORETICAL', 'Set true if only annotated transitions should be used and be corrected to the theoretical mz')        
        
        args_handler.add_app_args(log, 'TSV_MASS_LIMITS','Lower and Upper mass limits.')
        args_handler.add_app_args(log, 'TSV_ION_LIMITS','Min and Max number of reported ions per peptide/z')
        args_handler.add_app_args(log, 'TSV_PRECISION','Maximum error allowed at the annotation of a fragment ion')
        
        args_handler.add_app_args(log, 'TSV_REMOVE_DUPLICATES','Remove duplicate masses from labeling')        
        args_handler.add_app_args(log, 'TSV_EXACT','Use exact mass.')
        args_handler.add_app_args(log, 'TSV_GAIN','List of allowed fragment mass modifications. Useful for phosphorilation.')
        args_handler.add_app_args(log, 'TSV_CHARGE','Fragment ion charge states allowed.')
        args_handler.add_app_args(log, 'TSV_SERIES','List of ion series to be used')

        return args_handler
    
    def validate_run(self,info,log,run_code, out_stream, err_stream):
        if 0 != run_code:
            return run_code,info

        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' %self._result_file)
            return 1,info
        if not XmlValidator.is_wellformed(self._result_file):
            log.critical('[%s] is not well formed.' % self._result_file)
            return 1,info    
        return 0,info     

