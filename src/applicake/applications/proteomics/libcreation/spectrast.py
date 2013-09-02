"""
Created on Sep 29, 2012

@author: loblum
"""

import os
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils
from applicake.applications.proteomics.tpp.proteinprophetFDR import ProteinProphetFDR

class RawlibNodecoy(IWrapper):
    """
        Create raw text library without DECOYS_ from pepxml 
    """

    def prepare_run(self, info, log):
        #have to symlink the pepxml and mzxml files first into a single directory
        symlink_files = []
        if isinstance(info[Keys.PEPXMLS], list):
            raise Exception('found > 1 pepxml files [%s] in [%s].' % (len(info[Keys.PEPXMLS]), info[Keys.PEPXMLS]))
        else:
            symlink_files.append(info[Keys.PEPXMLS])

        if isinstance(info[Keys.MZXML], list):
            symlink_files.extend(info[Keys.MZXML])
        else:
            symlink_files.append(info[Keys.MZXML])

        for i, f in enumerate(symlink_files):
            dest = os.path.join(info[Keys.WORKDIR], os.path.basename(f))
            log.debug('create symlink [%s] -> [%s]' % (f, dest))
            os.symlink(f, dest)
            symlink_files[i] = dest

        #get iProb corresponding FDR for IDFilter
        info[Keys.IPROBABILITY] = ProteinProphetFDR().getiProbability(log, info)

        root = os.path.join(info[Keys.WORKDIR], 'RawlibNodecoy')
        self._result_file = info[Keys.SPLIB] = root + '.splib'
        command = "spectrast -c_BIN! -cf'Protein!~DECOY_' -cP%s -cI%s -cN%s %s" % (
        info[Keys.IPROBABILITY], info['MS_TYPE'], root, symlink_files[0])
        return command, info

    def set_args(self, log, args_handler):
        """
        See interface
        """
        args_handler.add_app_args(log, Keys.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, Keys.PEPXMLS, 'List of pepXML files', action='append')
        args_handler.add_app_args(log, Keys.MZXML, 'Peak list file in mzXML format', action='append')

        args_handler.add_app_args(log, Keys.PEPTIDEFDR, 'Peptide FDR cutoff (if no probability given)')
        args_handler.add_app_args(log, 'MS_TYPE', 'ms instrument type')

        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        """
        See super class.
        """
        if 0 != run_code:
            return run_code, info

        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' % self._result_file)
            return 1, info

        return 0, info


class RTcalibNoirt(IWrapper):
    """
        Filter out iRT peptides from RT calibrated spectral library
    """

    def prepare_run(self, info, log):
        self._orig_splib = info[Keys.SPLIB]

        root = os.path.join(info[Keys.WORKDIR], 'RTcalibNoirt')
        self._result_file = info[Keys.SPLIB] = root + '.splib'
        return "spectrast -c_BIN! -cf'Protein!~iRT' -cN%s %s" % (root, self._orig_splib), info

    def set_args(self, log, args_handler):
        """
        See interface
        """
        args_handler.add_app_args(log, Keys.SPLIB, 'Spectrast library in .splib format')
        args_handler.add_app_args(log, Keys.WORKDIR, 'Directory to store files')
        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        """
        See super class.
        """
        if 0 != run_code:
            return run_code, info

        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' % self._result_file)
            return 1, info

        return 0, info
