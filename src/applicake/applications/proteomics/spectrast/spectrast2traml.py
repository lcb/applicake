#!/usr/bin/env python
'''
Created on Mar 28, 2012

@author: loblum
'''

from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator

class Spectrast2TraML(IWrapper):
    """
    Wrapper for the famous spectrast2traml.sh script
    """
    def prepare_run(self,info,log):
        options = Spectrast2TraMLTemplate().modify_template(info, log) 
        if info.has_key('SWATH_WND_FILE'):
                options = options + " --swathfile " + info['SWATH_WND_FILE']
        self._result_file = info['LIBOUTBASE'] + '.TraML'
        return ('spectrast2traml.sh --in %s --out %s %s' % info[self.SPLIB],self._result_file,options)
    
    def set_args(self,log,args_handler):
        """
        See interface
        """        
        args_handler.add_app_args(log, self.SPLIB, 'Spectrast library in .splib format')
        args_handler.add_app_args(log, 'MAX_NR_TR', 'maximum nr of transitions per peptide')
        args_handler.add_app_args(log, 'MIN_NR_TR', 'min nr of transitions per peptide')
        args_handler.add_app_args(log, 'LOW_MZ_CUTOFF', 'lower mz limit/cutoff')
        args_handler.add_app_args(log, 'SWATH_WND_FILE', 'file containing swath windows')
        args_handler.add_app_args(log, 'SWDECOY_METHOD', 'decoy generation method (shuffle, pseudo-reverse, reverse, shift)')
        args_handler.add_app_args(log, 'LIBOUTBASE', 'Folder to put output libraries')
        return args_handler
    
    def validate_run(self,info,log,run_code, out_stream, err_stream):
        if 0 != run_code:
            return run_code,info
    #out_stream.seek(0)
    #err_stream.seek(0)
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' %self._result_file)
            return 1,info
        if not XmlValidator.is_wellformed(self._result_file):
            log.critical('[%s] is not well formed.' % self._result_file)
            return 1,info    
        return 0,info     


class Spectrast2TraMLTemplate(BasicTemplateHandler):
    """
    Template handler for Sptxt2Csv to generate a csv with all transitions (SRM mode).
    """

    def read_template(self, info, log):
        """
        See super class.
        """
        template = "--max_nr_tr $MAX_NR_TR --min_nr_tr $MIN_NR_TR --low_mz_cutoff $LOW_MZ_CUTOFF --method $SWDECOY_METHOD"
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info