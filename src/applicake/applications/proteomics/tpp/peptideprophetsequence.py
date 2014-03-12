#!/usr/bin/env python

"""
Created on Jan 22, 2013

@author: lorenz

Corrects pepxml output to make compatible with TPP and openms, then executes xinteract (step by step because of semiTrypsin option)

"""

import os
from applicake.applications.proteomics.tpp.searchengines.enzymes import enzymestr_to_engine

from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator
from applicake.applications.proteomics.tpp.pepxmlcorrector import PepXMLCorrector


class PeptideProphetSequence(IWrapper):
    def prepare_run(self, info, log):
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

        -p0 -dDECOY_ -OAPdlIw (dummy)
        """

        #CORRECT
        exit_code, info = PepXMLCorrector().main(info, log)
        if exit_code != 0:
            raise Exception("Could not correct pepxml")

        #XTINERACT
        info['XINTERACT'] = '-p0 -dDECOY_ -OAPdlIw'
        self._result_file = os.path.join(info[Keys.WORKDIR], 'interact.pep.xml')
        enz, _ = enzymestr_to_engine(info['ENZYME'],'InteractParser')
        command = """InteractParser %s %s -E%s &&
        RefreshParser %s %s &&
        PeptideProphetParser %s DECOY=DECOY_ ACCMASS NONPARAM DECOYPROBS LEAVE PI INSTRWARN MINPROB=0
        """ % (self._result_file, info[Keys.PEPXMLS][0], enz,
               self._result_file, info['DBASE'],
               self._result_file )
        return command, info

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

        info[Keys.PEPXMLS] = [self._result_file]
        return run_code, info
