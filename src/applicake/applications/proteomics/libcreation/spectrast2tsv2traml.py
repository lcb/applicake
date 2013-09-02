#!/usr/bin/env python
"""
Created on Mar 28, 2012

@author: loblum
"""

import os
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator


class Spectrast2TSV2traML(IWrapper):
    """
    Wrapper for the famous spectrast2traml.sh script
    """

    def prepare_run(self, info, log):

        insplib = info[Keys.SPLIB]
        consensuslib = os.path.join(info[Keys.WORKDIR], 'consensus')
        info[Keys.SPLIB] = consensuslib + '.splib'
        info['TSV'] = os.path.join(info[Keys.WORKDIR], 'spectrast2tsv.tsv')        
        info[Keys.TRAML] = os.path.join(info[Keys.WORKDIR], 'ConvertTSVToTraML.TraML')

        consensustype = ""  #None
        if info['CONSENSUS_TYPE'] == "Consensus":
            consensustype = "C"
        elif info['CONSENSUS_TYPE'] == "Best replicate":
            consensustype = "B"

        tsvopts = '-k openswath '
        tsvopts += ' -l ' + info['TSV_MASS_LIMITS'].replace("-", ",")
        mini, maxi = info['TSV_ION_LIMITS'].split("-")
        tsvopts += ' -o %s -n %s ' % (mini, maxi)
        tsvopts += ' -p ' + info['TSV_PRECISION']
        if info.has_key('TSV_REMOVE_DUPLICATES') and info['TSV_REMOVE_DUPLICATES'] == "True":
            tsvopts += ' -d'
        else:
            log.debug("no tsv rm duplicates")

        if info.has_key('TSV_EXACT') and info['TSV_EXACT'] == "True":
            tsvopts += ' -e'
        else:
            log.debug("no tsv exact")

        if info.has_key('TSV_CHARGE') and info['TSV_CHARGE'] != "":
            tsvopts += ' -x ' + info['TSV_CHARGE'].replace(";", ",")
        else:
            log.debug("no rm duplicates")

        if info.has_key('TSV_GAIN') and info['TSV_GAIN'] != "":
            tsvopts += ' -g ' + info['TSV_GAIN'].replace(";", ",")
        else:
            log.debug("no tsv gain")

        if info.has_key('TSV_SERIES') and info['TSV_SERIES'] != "":
            tsvopts += ' -s ' + info['TSV_SERIES'].replace(";", ",")
        else:
            log.debug("no tsv series")

        command = 'spectrast -c_BIN! -cA%s -cN%s %s && spectrast2tsv.py %s -a %s %s && tsv2traml.sh %s %s' % (
            consensustype, consensuslib, insplib,
            tsvopts, info['TSV'], info['SPLIB'],
            info['TSV'], info[Keys.TRAML])

        return command, info


    def set_args(self, log, args_handler):
        """
        See interface
        """
        args_handler.add_app_args(log, Keys.SPLIB, 'Spectrast library in .splib format')
        args_handler.add_app_args(log, Keys.WORKDIR, 'workdir')

        args_handler.add_app_args(log, Keys.PARAM_IDX, 'Parameter index to distinguish')

        args_handler.add_app_args(log, 'CONSENSUS_TYPE', 'consensus type cAC cAB')

        args_handler.add_app_args(log, 'TSV_MASS_LIMITS', 'Lower and Upper mass limits.')
        args_handler.add_app_args(log, 'TSV_ION_LIMITS', 'Min and Max number of reported ions per peptide/z')
        args_handler.add_app_args(log, 'TSV_PRECISION', 'Maximum error allowed at the annotation of a fragment ion')

        args_handler.add_app_args(log, 'TSV_REMOVE_DUPLICATES', 'Remove duplicate masses from labeling')
        args_handler.add_app_args(log, 'TSV_EXACT', 'Use exact mass.')
        args_handler.add_app_args(log, 'TSV_GAIN',
                                  'List of allowed fragment mass modifications. Useful for phosphorilation.')
        args_handler.add_app_args(log, 'TSV_CHARGE', 'Fragment ion charge states allowed.')
        args_handler.add_app_args(log, 'TSV_SERIES', 'List of ion series to be used')

        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        if 0 != run_code:
            return run_code, info

        if not FileUtils.is_valid_file(log, info[Keys.SPLIB]):
            log.critical('[%s] is not valid' % info[Keys.SPLIB])
            return 1, info
        if not FileUtils.is_valid_file(log, info['TSV']):
            log.critical('[%s] is not valid' % info['TSV'])
            return 1, info
        if not FileUtils.is_valid_file(log, info[Keys.TRAML]):
            log.critical('[%s] is not valid' % info[Keys.TRAML])
            return 1, info
        if not XmlValidator.is_wellformed(info[Keys.TRAML]):
            log.critical('[%s] is not well formed.' % info[Keys.TRAML])
            return 1, info
        return 0, info

