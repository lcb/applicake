#!/usr/bin/env python

'''
Created on Jan 22, 2013

@author: lorenz
'''

import os
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator

class PeptideProphetSequence(IWrapper):
    
    def prepare_run(self,info,log):
        #pepxmls always a list, even if only one pepxml
        pepxml_filename = info[self.PEPXMLS][0]        
        db_filename = info['DBASE']
        self._result_file  = os.path.join(info[self.WORKDIR], 'interact.pep.xml')
        
        omssafix = ''
        if info.has_key('OMSSAFIX'):
            omssafix = "-C -P"
            
        info['TEMPLATE'] = os.path.join(info[self.WORKDIR], 'interact.tpl')
        template,info = PeptideProphetSequenceTemplate().modify_template(info, log)
        paramarr = template.splitlines()
        
        cmds = []                
        # InteractParser <outfile> <file1.pep.xml> <file2.pep.xml>... <options>            
        cmds.append('InteractParser %s %s %s %s' % (self._result_file,pepxml_filename,paramarr[0],omssafix))
        # the 1st refreshparser is needed by myrimatch. otherwise no decays are found and no unsupervised model can be used
        #RefreshParser <xmlfile> <database>
        cmds.append('RefreshParser %s %s %s' % (self._result_file,db_filename,paramarr[1]))    
        #PeptideProphetParser output.pep.xml DECOY=DECOY_ MINPROB=0 NONPARAM
        cmds.append('PeptideProphetParser %s %s' % (self._result_file,paramarr[2]))           
        return ' && '.join(cmds),info
    
    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.PEPXMLS, 'List of pepXML files',action='append')
        args_handler.add_app_args(log, 'ENZYME', 'Enzyme used for digest')
        args_handler.add_app_args(log, 'DBASE', 'FASTA dbase')
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory')  
        args_handler.add_app_args(log, 'OMSSAFIX', 'Fix omssa',action="store_true")
        return args_handler
    
    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        """
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' %self._result_file)
            return 1,info
        if not XmlValidator.is_wellformed(self._result_file):
            log.critical('[%s] is not well formed.' % self._result_file)
            return 1,info  
        if not 'model complete after' in out_stream.read():
            log.error('PeptideProphet model did not complete.')
            return 1,info  
            
        info[self.PEPXMLS] = [self._result_file]         
        return run_code,info
          

class PeptideProphetSequenceTemplate(BasicTemplateHandler):
    """
    Template handler for xinteract.
    """
    def read_template(self, info, log):
        """
        See super class.
        """
        # Threads is not set by a variable as this does not make sense here
        template = """-L7 -E$ENZYME

DECOY=DECOY_ ACCMASS NONPARAM DECOYPROBS LEAVE PI INSTRWARN"""        
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info
        
