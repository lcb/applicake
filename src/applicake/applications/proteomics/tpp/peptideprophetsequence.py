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
        pepxml_filename = info[self.PEPXMLS]        
        db_filename = info['DBASE']
        self._result_filename  = os.path.join(self._wd, self.name  + '.pep.xml')
        if info.has_key('OMSSAFIX'):
            
        params,info = PeptideProphetSequenceTemplate().read_template(info, log)
        paramarr = params.splitlines()
        
        cmds = []                
        # InteractParser <outfile> <file1.pep.xml> <file2.pep.xml>... <options>            
        cmds.append('InteractParser %s %s %s' % (self._result_filename,pepxml_filename,paramarr[0]))
        # the 1st refreshparser is needed by myrimatch. otherwise no decays are found and no unsupervised model can be used
        #RefreshParser <xmlfile> <database>
        cmds.append('RefreshParser %s %s %s' % (self._result_filename,db_filename,paramarr[1]))    
        #PeptideProphetParser output.pep.xml DECOY=DECOY_ MINPROB=0 NONPARAM
        cmds.append('PeptideProphetParser %s %s' % (self._result_filename,paramarr[2]))           
        return ' && '.join(cmds)
    
    def set_args(self):
        pass
    
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
        if not 'model complete after' in out_stream:
            log.error('PeptideProphet model did not complete.')
            return 1,info           
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
        template = """
-L7 -E$ENZYME $OMSSAFIX

DECOY=DECOY_ ACCMASS NONPARAM DECOYPROBS LEAVE PI INSTRWARN MINPROB=0
"""        
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info
        