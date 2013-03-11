'''
Created on Jul 11, 2012

@author: quandtan
'''

import os
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator

class ChromatogramExtractor(IWrapper):
    '''
    Wrapper for the ChromatogramExtractor of OpenSWATH.
    '''

    _template_file = ''
    _default_prefix = 'OpenSwathChromatogramExtractor'

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._template_file = '%s.tpl' % base # application specific config file
        #self._file_suffix = '_rtnorm.chrom.mzML'

    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def prepare_run(self,info,log):
        """
        See interface.

        - Define path to result file (depending on work directory)
        - If a template is used, the template is read variables from the info object are used to set concretes.
        - If there is a result file, it is added with a specific key to the info object.
        """
        self.outfile = os.path.join(info[self.WORKDIR],'ChromatogramExtractor.chrom.mzML')
        info['CHROM_MZML'] = self.outfile
        prefix,info = self.get_prefix(info,log)
        ppm = ''
        if info['WINDOW_UNIT'] == 'ppm':
            ppm = '-ppm'
        
        trafoxml = ''
        if 'TRAFOXML' in info:
            log.info("Using TrafoXML" + info['TRAFOXML'] )
            trafoxml = '-rt_norm ' + info['TRAFOXML']
            
        command = '%s -in %s -extraction_window %s %s -rt_extraction_window %s -tr %s -min_upper_edge_dist %s -threads %s -is_swath -out %s %s' % (prefix,
                                                                                              ' '.join(info['MZML']),
                                                                                              info['EXTRACTION_WINDOW'],
                                                                                              ppm,
                                                                                              info['RT_EXTRACTION_WINDOW'],
                                                                                              info['TRAML'],
                                                                                              info['MIN_UPPER_EDGE_DIST'],
                                                                                              info['THREADS'],
                                                                                              self.outfile,trafoxml)
        return command,info

    def set_args(self,log,args_handler):
        """
        See super class.

        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, 'THREADS', 'Number of threads used in the process.') 
        args_handler.add_app_args(log, 'TRAML', 'Path to the TraML file.')
        args_handler.add_app_args(log, 'MZML', 'Comma separated list of the mzML(.gz) files.')
        args_handler.add_app_args(log, 'MIN_UPPER_EDGE_DIST', 'minimum upper edge distance parameter')
        args_handler.add_app_args(log, 'EXTRACTION_WINDOW', 'extraction window to extract around')
        args_handler.add_app_args(log, 'WINDOW_UNIT','extraction window unit thompson/ppm')
        args_handler.add_app_args(log, 'RT_EXTRACTION_WINDOW', 'RT extraction window to extract around')
        args_handler.add_app_args(log, 'TRAFOXML', 'TrafoXML')
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        """
        if 0 != run_code:
            return run_code,info
    #out_stream.seek(0)
    #err_stream.seek(0)
        if not FileUtils.is_valid_file(log, self.outfile):
            log.critical('[%s] is not valid' %self.outfile)
            return 1,info
        if not XmlValidator.is_wellformed(self.outfile):
            log.critical('[%s] is not well formed.' % self.outfile)
            return 1,info    
        return 0,info

class IRTChromatogramExtractor(ChromatogramExtractor):
    
    def prepare_run(self,info,log):
        self._traml = info['TRAML']
        info['TRAML'] = info['IRTTRAML']
        self._rtwnd = info['RT_EXTRACTION_WINDOW']
        info['RT_EXTRACTION_WINDOW'] = '-1'
        command, info = super(IRTChromatogramExtractor, self).prepare_run(info,log)
        return command,info
    
    def validate_run(self,info,log, run_code,out_stream, err_stream):
        info['TRAML'] = self._traml
        info['RT_EXTRACTION_WINDOW'] = self._rtwnd 
        return super(IRTChromatogramExtractor, self).validate_run(info,log, run_code,out_stream, err_stream)
     
    def set_args(self,log,args_handler):  
        args_handler = super(IRTChromatogramExtractor, self).set_args(log,args_handler)
        args_handler.add_app_args(log, 'IRTTRAML', 'Path to the iRT TraML file.')
        return args_handler
