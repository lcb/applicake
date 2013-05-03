'''
Created on Jul 11, 2012

@author: quandtan
'''

import os
from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator

class OpenSwathRTNormalizerParallel(IWrapper):
    '''
    Wrapper for the OpenSwathRTNormalizer in OpenSWATH.
    '''

    def prepare_run(self,info,log):
        
        #wow python can do ternary operator
        ppm = '-ppm' if info['WINDOW_UNIT'] == 'ppm' else ''

        ceopts = '-extraction_window %s %s -rt_extraction_window -1 -tr %s -min_upper_edge_dist %s -is_swath' % (
                     info['EXTRACTION_WINDOW'],
                     ppm,
                     info['IRTTRAML'],
                     info['MIN_UPPER_EDGE_DIST'])
        rtopts = '-tr %s -min_rsq %s -min_coverage %s' % (info['IRTTRAML'],info['MIN_RSQ'],info['MIN_COVERAGE'])
        
        command = 'OpenSwathRTNormalizerParallel.sh -t %s -c "%s" -r "%s" -o %s %s' % (info['THREADS'],ceopts,rtopts,info[self.WORKDIR]," ".join(info['MZML']))
        return command, info

    def set_args(self,log,args_handler):
        """
        See super class.
        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, 'THREADS', 'Number of threads used in the process.') 
        args_handler.add_app_args(log, 'IRTTRAML', 'Path to the iRT TraML file.')
        args_handler.add_app_args(log, 'MZML', 'Path to the mzMLs')
        args_handler.add_app_args(log, 'MIN_RSQ', '') 
        args_handler.add_app_args(log, 'MIN_COVERAGE', '')
        args_handler.add_app_args(log, 'MIN_UPPER_EDGE_DIST', 'minimum upper edge distance parameter')
        args_handler.add_app_args(log, 'EXTRACTION_WINDOW', 'extraction window to extract around')
        args_handler.add_app_args(log, 'WINDOW_UNIT','extraction window unit thompson/ppm')
        args_handler.add_app_args(log, 'RT_EXTRACTION_WINDOW', 'RT extraction window to extract around')
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        """
        if 0 != run_code:
            return run_code,info
        
        for line in out_stream:
            outfile=line
        info["TRAFOXML"] = outfile.strip()
        
        if not FileUtils.is_valid_file(log, info["TRAFOXML"]):
            log.critical('[%s] is not valid' %info["TRAFOXML"])
            return 1,info
        if not XmlValidator.is_wellformed(info["TRAFOXML"]):
            log.critical('[%s] is not well formed.' % info["TRAFOXML"])
            return 1,info    
        return 0,info
