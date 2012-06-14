'''
Created on May 28, 2012

@author: quandtan
'''
import os
from applicake.applications.proteomics.base import MsMsIdentification
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator

class Omssa(MsMsIdentification):
    '''
    Wrapper for the search engine OMSSA.
    '''
    
    _result_file = 'omssa.pep.xml'

    def prepare_run(self,info,log):
        """
        See interface
        """         
        log.debug('get template handler')
        th = self.get_template_handler()
        log.debug('modify template')                
        mod_tpl,info = th.modify_template(info, log)      
        prefix,info = self.get_prefix(info,log)
#        basename = info['MGF'].split(".")[0].split("/")[-1]        
#        _result_file  = os.path.join(info[self.WORKDIR],basename + ".pep.xml")
        self._result_file = os.path.join(info[self.WORKDIR],self._result_file)
        command = "%s %s -fm %s -op %s" %(prefix,mod_tpl,info['MGF'],self._result_file)
        return command,info          
        
    def set_args(self,log,args_handler):
        """
        See interface
        """        
        args_handler = super(Omssa, self).set_args(log,args_handler)
        args_handler.add_app_args(log, 'MGF', 'Peak list file in mgf format')         
        return args_handler  

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        
        Check the following:
        - each line of stdout start with 'Info'
        - result file is valid
        - result file is a well-formed xml
        """  
        exit_code,info = super(Omssa,self).validate_run(info,log, run_code,out_stream, err_stream)
        if 0 != run_code:
            return exit_code,info   
        out_stream.seek(0)  
        for line in out_stream.read_lines():
            if not line.startswith('Info:'):
                self.log.critical("stderr contains following line [%s]" % line)
                return 1,info        
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' %self._result_file)
        if not XmlValidator.is_wellformed(self._result_file):
            log.critical('[%s] is not well formed.' % self._result_file)
            return 1,info
        return 0,info        
        
class OmssaTemplate(BasicTemplateHandler):
    """
    Template handler for Omssa.  
    """
    def read_template(self, info, log):
        """
        See super class.
        """  
        template = """-nt $THREADS -d $DBASE -e 0 -v $MISSEDCLEAVAGE -mf 3 -he 100000.0 -zcc 1 -ii 0 -te $PRECMASSERR -to $FRAGMASSERR -ht 6 -hm 2 -ir 0 -h1 100 -h2 100 -hl 1"""
        log.debug('read template from [%s]' % self.__class__.__name__)
        if info['PRECMASSUNIT'].lower() == "ppm":
            template = template + ' -teppm'
            self.log.debug('added [ -teppm] to template')
        return template,info
