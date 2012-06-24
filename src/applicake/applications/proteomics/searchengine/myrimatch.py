'''
Created on Jun 24, 2012

@author: quandtan
'''

import os
from applicake.applications.proteomics.base import MsMsIdentification
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator

class Myrimatch(MsMsIdentification):
    """
    Wrapper for the search engine Myrimatch.
    """

    MYRIMATCH_MINTERMINICLEAVAGES = 'MinTerminiCleavages'

    def __init__(self):
        """
        Constructor
        """
        super(Myrimatch,self).__init__()
        base = self.__class__.__name__
        self._result_file = '%s.pepXML' % base # result produced by the application
        
        
    def define_enzyme(self,info,log):
        """
        See super class.
        
        For Myrimatch, the method has to additionally set the number of MinTerminiCleavages
        """
        info = super(Myrimatch,self).define_enzyme(info,log)        
        enzyme_info = info[self.ENZYME].split(':')
        info[self.ENZYME] = enzyme_info[0]
        info[self.MYRIMATCH_MINTERMINICLEAVAGES] = enzyme_info[1]
        return info        

    def _get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = 'myrimatch'
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def get_template_handler(self):
        """
        See interface
        """
        return MyrimatchTemplate()

    def prepare_run(self,info,log):
        """
        See interface.
        
        - Read the template from the handler
        - Convert modifications into the specific format
        - Convert enzyme into the specific format
        - modifies the template from the handler 
        """
        wd = info[self.WORKDIR]
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        self._template_file = os.path.join(wd,self._template_file) 
        info['TEMPLATE'] = self._template_file
        self._result_file = os.path.join(wd,self._result_file) 
        info['PEPXMLS'] = [self._result_file]
        log.debug('define modifications')
        info = self.define_mods(info, log)
        log.debug('define enzyme')
        info = self.define_enzyme(info, log)        
        log.debug('get template handler')
        th = self.get_template_handler()
        if info['FRAGMASSUNIT'] == 'Da':
            self.log.debug("replace 'FRAGMASSUNIT' with value [Da] to [daltons]")
            info['FRAGMASSUNIT'] ='daltons'            
        log.debug('modify template')
        mod_template,info = th.modify_template(info, log)              
        prefix,info = self._get_prefix(info,log)
        command = "%s %s %s " %(prefix,mod_template,self._result_file)
        # myrimatch -ProteinDatabase AE004092_sp_9606.fasta B08-02057_p.mzXML 
        return "%s -cpus %s -cfg %s -workdir %s -ProteinDatabase %s %s" %(prefix,info['THREADS'],info['TEMPLATE'],
                                                                          info[self.WORKDIR], info['DBASE'],
                                                                          info['MZXML'])        
        
        return command,info

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler = super(Myrimatch, self).set_args(log,args_handler)
        args_handler.add_app_args(log, 'MZXML', 'Peak list file in mzXML format')
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.

        Check the following:
        -
        """
        exit_code,info = super(Myrimatch,self).validate_run(info,log, run_code,out_stream, err_stream)
        if 0 != run_code:
            return exit_code,info
        out_stream.seek(0)
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' %self._result_file)
            return 1,info
        if not XmlValidator.is_wellformed(self._result_file):
            log.critical('[%s] is not well formed.' % self._result_file)
            return 1,info
        return 0,info


class MyrimatchTemplate(BasicTemplateHandler):
    """
    Template handler for Myrimatch.
    """

    def read_template(self, info, log):
        """
        See super class.
        """
        template = """DecoyPrefix = ""
MonoPrecursorMzTolerance = $PRECMASSERR $PRECMASSUNIT
FragmentMzTolerance = $FRAGMASSERR $FRAGMASSUNIT

PrecursorMzToleranceRule = "mono"
FragmentationRule= "cid"
FragmentationAutoRule = false
NumIntensityClasses = 3
ClassSizeMultiplier = 2

NumChargeStates = 5
UseSmartPlusThreeModel = true
TicCutoffPercentage = 0.95

CleavageRules = "$ENZYME
MaxMissedCleavages = $MISSEDCLEAVAGE
MinTerminiCleavages = $MINTERMINICLEAVAGES 
MinPeptideLength =  5
MaxPeptideLength = 75
MaxPeptideMass = 6500
MinPeptideMass = 400
DynamicMods = "$VARIABLE_MODS"
MaxDynamicMods = 4
StaticMods = "$STATIC_MODS"
MaxResultRank = 1
ComputeXCorr = true
NumBatches = 50
ThreadCountMultiplier = 10
UseMultipleProcessors = true
"""