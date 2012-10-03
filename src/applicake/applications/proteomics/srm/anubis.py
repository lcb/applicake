#!/usr/bin/env python
'''
Created on Oct 3, 2012

@author: johant
'''

from applicake.framework.interfaces import IWrapper
from applicake.framework.argshandler import ArgsHandler

class Anubis(IWrapper):
    """
    Runs anubis
    """
    
    NULL_DIST_SIZE      = 'NULL_DIST_SIZE'
    MAX_NUM_TRANSITIONS = 'MAX_NUM_TRANSITIONS'
    PEAK_MIN_WIDTH      = 'PEAK_MIN_WIDTH'
    REFERENCE_FILE      = 'REFERENCE_FILE'
    ANUBIS_VERSION      ='ANUBIS_VERSION'
    
    
    
    def prepare_run(self,info,log):
        """
        See interface
        """
        cmd = "java -jar anubis.jar "
        info[self.ANUBIS_VERSION] = "1.0.6"
        
        if self.NULL_DIST_SIZE in info:
            cmd += "--null-dist=%i " % info[self.NULL_DIST_SIZE]
        else:
            info[self.NULL_DIST_SIZE] = 1000
        
        if self.MAX_NUM_TRANSITIONS in info:
            cmd += "--trans-limit=%i " % info[self.MAX_NUM_TRANSITIONS]
        else:
            info[self.MAX_NUM_TRANSITIONS] = 6
        
        if self.REFERENCE_FILE not in info:
            log.fatal('did not find the required %s key' % self.REFERENCE_FILE)
            return ''
        cmd += '%s ' % info['REFERENCE_FILE']
        
        if self.PEAK_MIN_WIDTH in info:
            cmd += "%d " % info[self.PEAK_MIN_WIDTH]
        else:
            cmd += "0.1 "
            info[self.PEAK_MIN_WIDTH] = 0.1
            
        if self.OUTPUT not in info:
            log.fatal('did not find the required %s key' % self.OUTPUT)
            return ''
        cmd += '%s ' % info['OUTPUT']
            
        if self.MZML not in info:
            log.fatal('did not find the required %s key' % self.MZML)
            return ''
        cmd += '%s ' % info['MZML']
        
        return (cmd, info)
    
    
    
    def set_args(self,log,args_handler):
        """
        See interface
        """        
        args_handler.add_app_args(log, self.NULL_DIST_SIZE, 
            'size of null distrubution for each chromatogram (int > 0, default: 1000)')
        args_handler.add_app_args(log, self.MAX_NUM_TRANSITIONS, 
            'limit on the number of transitions used (int > 2, default: 6)')
        args_handler.add_app_args(log, self.PEAK_MIN_WIDTH, 
            'minimum expected peak width in minutes (float > 0.0, default: 0.1)')
        args_handler.add_app_args(log, self.REFERENCE_FILE, 
            'traml file with reference transition intensities')
        return args_handler
    
    
    
    def validate_run(self,info,log,run_code, out_stream, err_stream):
        """
        See interface
        """
        if run_code != 0:
            exit_code = run_code
        else:
            try:
                f = open(info['OUTPUT'], 'r')
                f.close()
                exit_code = 0
            except:
                log.error('No output file was created. check key [OUTPUT]')
                exit_code = 1
                
        return (exit_code, info)
