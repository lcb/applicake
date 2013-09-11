"""
Created on Jun 24, 2012

@author: quandtan
"""

import os
from applicake.framework.keys import Keys
from applicake.applications.proteomics.tpp.searchengines.base import SearchEngine
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator


class Myrimatch(SearchEngine):
    """
    Wrapper for the search engine Myrimatch.
    """

    MYRIMATCH_MINTERMINICLEAVAGES = 'MYRIMATCH_MINTERMINICLEAVAGES'

    def __init__(self):
        """
        Constructor
        """
        super(Myrimatch, self).__init__()

    def define_enzyme(self, info, log):
        """
        See super class.
        
        For Myrimatch, the method has to additionally set the number of MinTerminiCleavages
        """
        info = super(Myrimatch, self).define_enzyme(info, log)
        enzyme_info = info[self.ENZYME].split(':')
        log.debug('enzyme info: [%s]' % enzyme_info)
        info[self.ENZYME] = enzyme_info[0]
        info[self.MYRIMATCH_MINTERMINICLEAVAGES] = enzyme_info[1]
        return info

    def define_mods(self, info, log):
        """
        Convert generic static/variable modifications into the myrimatch-specific format
        """
        info = super(Myrimatch, self).define_mods(info, log)
        if info.has_key(self.STATIC_MODS):
            info[self.STATIC_MODS] = info[self.STATIC_MODS].replace(',', ' ')
        if info.has_key(self.VARIABLE_MODS):
            info[self.VARIABLE_MODS] = info[self.VARIABLE_MODS].replace(' ', ' * ')
            info[self.VARIABLE_MODS] = info[self.VARIABLE_MODS].replace(',', ' ')
        return info


    def _get_prefix(self, info, log):
        if not info.has_key(Keys.PREFIX):
            info[Keys.PREFIX] = 'myrimatch'
            log.debug('set [%s] to [%s] because it was not set before.' % (Keys.PREFIX, info[Keys.PREFIX]))
        return info[Keys.PREFIX], info

    def get_template_handler(self):
        """
        See interface
        """
        return MyrimatchTemplate()

    def prepare_run(self, info, log):
        """
        See interface.
        
        - Read the template from the handler
        - Convert modifications into the specific format
        - Convert enzyme into the specific format
        - modifies the template from the handler 
        """
        wd = info[Keys.WORKDIR]
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        self._template_file = os.path.join(wd, self._template_file)
        info['TEMPLATE'] = self._template_file
        basename = os.path.splitext(os.path.split(info['MZXML'])[1])[0]
        self._result_file = os.path.join(wd, basename + ".pepXML") #myrimatch default is pepXML NOT pep.xml
        info[Keys.PEPXMLS] = [self._result_file]
        # need to create a working copy to prevent replacement or generic definitions
        # with app specific definitions
        app_info = info.copy()
        log.debug('define modifications')
        app_info = self.define_mods(app_info, log)
        log.debug('define enzyme')
        app_info = self.define_enzyme(app_info, log)
        log.debug('get template handler')
        th = self.get_template_handler()
        if app_info['FRAGMASSUNIT'] == 'Da':
            log.debug("replace 'FRAGMASSUNIT' with value [Da] to [daltons]")
            app_info['FRAGMASSUNIT'] = 'daltons'
        log.debug('modify template')
        mod_template, app_info = th.modify_template(app_info, log)

        prefix, info = self._get_prefix(info, log)
        command = "%s -cpus %s -cfg %s -workdir %s -ProteinDatabase %s %s" % (
        prefix, app_info['THREADS'], app_info['TEMPLATE'],
        app_info[Keys.WORKDIR], app_info['DBASE'],
        app_info['MZXML'])
        # update original info object with new keys from working copy
        #info = DictUtils.merge(log, info, app_info, priority='left')        
        return command, info

    def set_args(self, log, args_handler):
        """
        See interface
        """
        args_handler = super(Myrimatch, self).set_args(log, args_handler)
        args_handler.add_app_args(log, 'MZXML', 'Peak list file in mzXML format')
        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        """
        See super class.

        Check the following:
        -
        """
        exit_code, info = super(Myrimatch, self).validate_run(info, log, run_code, out_stream, err_stream)
        if 0 != run_code:
            return exit_code, info
        out_stream.seek(0)
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' % self._result_file)
            return 1, info
        if not XmlValidator.is_wellformed(self._result_file):
            log.critical('[%s] is not well formed.' % self._result_file)
            return 1, info
        return 0, info


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

CleavageRules = "$ENZYME"
MaxMissedCleavages = $MISSEDCLEAVAGE
MinTerminiCleavages = $MYRIMATCH_MINTERMINICLEAVAGES 
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
UseMultipleProcessors = true
"""
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template, info
