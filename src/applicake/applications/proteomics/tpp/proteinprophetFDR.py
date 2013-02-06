'''
Created on Jun 18, 2012

@author: loblum
'''

import os
import sys
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator

class ProteinProphetFDR(IWrapper):
    '''
    Wrapper for TPP-tool ProteinProphet.
    '''

    _template_file = ''
    _result_file = ''
    _default_prefix = 'ProteinProphet'

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._template_file = '%s.tpl' % base # application specific config file
        self._result_file = '%s.prot.xml' % base # result produced by the application

    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def get_template_handler(self):
        """
        See interface
        """
        return ProtProphetFDRTemplate()

    def getiProbability(self,log,info):
        minprob = ''
        for line in open(info['PEPXMLS']):
            if line.startswith('<error_point error="%s' % info['FDR']):
                minprob = line.split(" ")[2].split("=")[1].replace('"','')
                break
            
        if minprob != '':
            log.info("Found minprob %s for FDR %s" % (minprob,info['FDR']) ) 
        else:
            log.fatal("error point for FDR %s not found" % info['FDR'])
            raise Exception("FDR not found")
        return minprob
    
    
    def prepare_run(self,info,log):
        if len(info['PEPXMLS']) > 1:
            log.fatal("This ProteinProphet only takes one iProphet inputfile!")
            return 1,info
        
        # store original values in temporary key
        info['ORGPEPXMLS'] = info['PEPXMLS']
        # creates a stringlist with ' ' as separator 
        info['PEPXMLS'] = info['PEPXMLS'][0]
        info['PROBABILITY'] = self.getiProbability(log,info)         
        wd = info[self.WORKDIR]
        self._result_file = os.path.join(wd,self._result_file)
        info['PROTXML'] = self._result_file
        self._template_file = os.path.join(wd,self._template_file)
        info['TEMPLATE'] = self._template_file
        log.debug('get template handler')
        th = self.get_template_handler()
        log.debug('modify template')
        mod_template,info = th.modify_template(info, log)
        
        # revert temporary key
        info[self.PEPXMLS] = info['ORGPEPXMLS']
        del info['ORGPEPXMLS'] 
        prefix,info = self.get_prefix(info,log)
        command = '%s %s' % (prefix,mod_template)
        return command,info

    def set_args(self,log,args_handler):
        """
        See super class.

        Set several arguments shared by the different search engines
        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, self.TEMPLATE, 'Path to the template file')
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory')  
        args_handler.add_app_args(log, self.PEPXMLS, 'Single iProphet inputfile',action='append')
        args_handler.add_app_args(log, self.FDR, 'FDR cutoff')
        
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        """
        #err_stream.seek(0)
        out_stream.seek(0)
        stdout = out_stream.read()
        msg = 'No xml file specified; please use the -file option'
        if msg in stdout:
                log.debug('ProteinProphet ignore [%s] of protxml2html' % msg)               
        for msg in ['did not find any InterProphet results in input data!',
                    'no data - quitting',
                    'WARNING: No database referenced']:
            if msg in stdout:
                log.error('ProteinProphet error [%s]' % msg)
                return 1,info
            else:
                log.debug('ProteinProphet: passed check [%s]' % msg)
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' %self._result_file)
            return 1,info
        if not XmlValidator.is_wellformed(self._result_file):
            log.critical('[%s] is not well formed.' % self._result_file)
            return 1,info             
        return 0,info


class ProtProphetFDRTemplate(BasicTemplateHandler):
    """
    Template handler for ProteinProphet.
    
    Calculations are done on iprophet score.
    """

    def read_template(self, info, log):
        """
        See super class.
        """
        template = """$PEPXMLS $PROTXML IPROPHET MINPROB$PROBABILITY
"""
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info
