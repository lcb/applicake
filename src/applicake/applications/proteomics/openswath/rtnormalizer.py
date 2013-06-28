"""
Created on Jul 11, 2012

@author: quandtan
"""

import os
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator


class OpenSwathRTNormalizer(IWrapper):
    """
    Wrapper for the MRMRTNormalizer in OpenSWATH.
    """

    def prepare_run(self, info, log):
        basename = info['CHROM_MZML'][0].split("split_")[1]
        basename = basename.split(".chrom.mzML")[0]
        info['TRAFOXML'] = os.path.join(info[Keys.WORKDIR], basename + '.trafoXML')
        mergedchrom = os.path.join(info[Keys.WORKDIR], 'merged.chrom.mzML')

        command = "FileMerger -in %s -out %s && " \
                  "OpenSwathRTNormalizer -tr %s -min_rsq %s -min_coverage %s -in %s -out %s" % \
                  (" ".join(info['CHROM_MZML']), mergedchrom,
                   info['IRTTRAML'], info['MIN_RSQ'], info['MIN_COVERAGE'], mergedchrom, info['TRAFOXML'])
        return command, info

    def set_args(self, log, args_handler):
        """
        See super class.
        """
        args_handler.add_app_args(log, Keys.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, Keys.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, 'THREADS', 'Number of threads used in the process.')
        args_handler.add_app_args(log, 'IRTTRAML', 'Path to the TraML file.')
        args_handler.add_app_args(log, 'CHROM_MZML', 'Path to the chrom.mzML after filemerger files.')
        args_handler.add_app_args(log, 'MIN_RSQ', '')
        args_handler.add_app_args(log, 'MIN_COVERAGE', '')
        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        """
        See super class.
        """
        if 0 != run_code:
            return run_code, info
        outfile = info['TRAFOXML']
        if not FileUtils.is_valid_file(log, outfile):
            return 1, info
        if not XmlValidator.is_wellformed(outfile):
            return 1, info
        return 0, info
