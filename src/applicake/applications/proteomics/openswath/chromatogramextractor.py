"""
Created on Jul 11, 2012

@author: quandtan
"""

import os
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator


class OpenSwathChromatogramExtractor(IWrapper):
    """
    Wrapper for the OpenSwathChromatogramExtractor of OpenSWATH.
    """

    def prepare_run(self, info, log):
        ppm = ''
        if info['WINDOW_UNIT'] == 'ppm':
            ppm = '-ppm'

        trafoxml = ''
        if 'TRAFOXML' in info:
            log.info("Using TrafoXML" + info['TRAFOXML'])
            trafoxml = '-rt_norm ' + info['TRAFOXML']

        #outfiles will be here
        info["CHROM_MZML"] = []
        for i in info['MZML']:
            info["CHROM_MZML"].append(os.path.join(info[Keys.WORKDIR],os.path.basename(i).replace("mzML.gz","chrom.mzML")))
        
        command = """for i in %s;
        do root=$(basename $i .mzML.gz);
        echo %s -no_progress -is_swath -extraction_window %s %s -rt_extraction_window %s -tr %s -min_upper_edge_dist %s %s -in $i -out %s/$root.chrom.mzML;
        done | parallel -t -j %s --halt 2""" % \
        (' '.join(info['MZML']),
         info['PREFIX'],info['EXTRACTION_WINDOW'],ppm, info['RT_EXTRACTION_WINDOW'],info['TRAML'], info['MIN_UPPER_EDGE_DIST'], trafoxml, info[Keys.WORKDIR],
         info['THREADS'])

        return command, info

    def set_args(self, log, args_handler):
        """
        See super class.
        """
        args_handler.add_app_args(log, Keys.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, Keys.PREFIX, 'Path to the executable',default='OpenSwathChromatogramExtractor')
        args_handler.add_app_args(log, 'THREADS', 'Number of threads used in the process.')
        args_handler.add_app_args(log, 'TRAML', 'Path to the TraML file.')
        args_handler.add_app_args(log, 'MZML', 'Comma separated list of the mzML(.gz) files.')
        args_handler.add_app_args(log, 'MIN_UPPER_EDGE_DIST', 'minimum upper edge distance parameter')
        args_handler.add_app_args(log, 'EXTRACTION_WINDOW', 'extraction window to extract around')
        args_handler.add_app_args(log, 'WINDOW_UNIT', 'extraction window unit thompson/ppm')
        args_handler.add_app_args(log, 'RT_EXTRACTION_WINDOW', 'RT extraction window to extract around')
        args_handler.add_app_args(log, 'TRAFOXML', 'TrafoXML if available')
        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):

        if 0 != run_code:
            return run_code, info

        for outfile in info['CHROM_MZML']:
            if not FileUtils.is_valid_file(log, outfile):
                log.critical('[%s] is not valid' % outfile)
                return 1, info
            if not XmlValidator.is_wellformed(outfile):
                log.critical('[%s] is not well formed.' % outfile)
                return 1, info

        return 0, info


class IRTChromatogramExtractor(OpenSwathChromatogramExtractor):
    """
    IRT OpenSwathChromatogramExtractor subclass of original ChromExtract
    """
    def prepare_run(self, info, log):
        self._traml = info['TRAML']
        info['TRAML'] = info['IRTTRAML']
        self._rtwnd = info['RT_EXTRACTION_WINDOW']
        info['RT_EXTRACTION_WINDOW'] = '-1'
        command, info = super(IRTChromatogramExtractor, self).prepare_run(info, log)
        return command, info

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        info['TRAML'] = self._traml
        info['RT_EXTRACTION_WINDOW'] = self._rtwnd
        return super(IRTChromatogramExtractor, self).validate_run(info, log, run_code, out_stream, err_stream)

    def set_args(self, log, args_handler):
        args_handler = super(IRTChromatogramExtractor, self).set_args(log, args_handler)
        args_handler.add_app_args(log, 'IRTTRAML', 'Path to the iRT TraML file.')
        return args_handler
