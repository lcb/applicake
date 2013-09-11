#!/usr/bin/env python

"""
Created on Jan 22, 2013

@author: lorenz

Corrects pepxml output to make compatible with TPP and openms, then executes xinteract (step by step because of semiTrypsin option)

"""

import os
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator
from applicake.applications.proteomics.tpp.pepxmlcorrector import PepXMLCorrector


class PeptideProphetSequence(IWrapper):
    def prepare_run(self, info, log):

        #CORRECT
        exit_code, info = PepXMLCorrector().main(info, log)
        if exit_code != 0:
            raise Exception("Could not correct pepxml")

        #XTINERACT        
        self._result_file = os.path.join(info[Keys.WORKDIR], 'interact.pep.xml')
        db_filename = info['DBASE']
        
        info['TEMPLATE'] = os.path.join(info[Keys.WORKDIR], 'interact.tpl')
        template, info = PeptideProphetSequenceTemplate().modify_template(info, log)
        paramarr = template.splitlines()

        cmds = []
        cmds.append('InteractParser %s %s %s' % (self._result_file, info[Keys.PEPXMLS][0], paramarr[0]))
        cmds.append('RefreshParser %s %s %s' % (self._result_file, db_filename, paramarr[1]))
        cmds.append('PeptideProphetParser %s %s' % (self._result_file, paramarr[2]))
        return ' && '.join(cmds), info

    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, Keys.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, Keys.PEPXMLS, 'List of pepXML files', action='append')
        args_handler.add_app_args(log, 'ENZYME', 'Enzyme used for digest')
        args_handler.add_app_args(log, 'DBASE', 'FASTA dbase')
        args_handler.add_app_args(log, 'MZXML', 'Path to the original MZXML inputfile')
        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        """
        See super class.
        """
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' % self._result_file)
            return 1, info
        if not XmlValidator.is_wellformed(self._result_file):
            log.critical('[%s] is not well formed.' % self._result_file)
            return 1, info

        #out_stream.seek(0)   
        #if not 'model complete after' in out_stream.read():
        #    log.error('PeptideProphet model did not complete.')
        #    return 1, info

        info[Keys.PEPXMLS] = [self._result_file]
        return run_code, info


class PeptideProphetSequenceTemplate(BasicTemplateHandler):
    """
    Template handler for xinteract. mapping of options:
    -p0 MINPROB=0
    -dDECOY_ DECOY=DECOY_ str used for decoys
    -OA ACCMASS accurate mass binning
    -OP NONPARAM
    -Od DECOYPROBS
    -Ol LEAVE
    -OI PI
    -Ow INSTRWARN
    """

    def read_template(self, info, log):
        """
        See super class.
        """
        template = """-L7 -E$ENZYME

DECOY=DECOY_ ACCMASS NONPARAM DECOYPROBS LEAVE PI INSTRWARN MINPROB=0"""
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template, info
        
