#!/usr/bin/env python
'''
Created on Oct 3, 2012

@author: johant
'''

import subprocess
import shlex
import re

from applicake.framework.interfaces import IWrapper
from applicake.framework.argshandler import ArgsHandler

class AnubisException(Exception):
    def __init__(self, mess):
        self.mess = mess

class Anubis(IWrapper):
    """
    Runs anubis
    """
    
    NULL_DIST_SIZE      = 'ANUBIS_NULL_DIST_SIZE'
    MAX_NUM_TRANSITIONS = 'ANUBIS_MAX_NUM_TRANSITIONS'
    PEAK_MIN_WIDTH      = 'ANUBIS_PEAK_MIN_WIDTH'
    SINGLE_ANSWER       = 'ANUBIS_SINGLE_ANSWER'
    P_VALUE_TOLERANCE   = 'ANUBIS_P_VALUE_TOLERANCE'
    VERSION             = 'ANUBIS_VERSION'
    JVM                 = 'ANUBIS_JVM'
    JVM_VERSION         = 'ANUBIS_JVM_VERSION'
    MAX_HEAP_SIZE       = 'ANUBIS_MAX_HEAP_SIZE'
    OUTPUT_RESULT_FILE  = 'ANUBIS_OUTPUT'
    TRAML               = 'TRAML'
    
    DEFAULT_JVM         = '/usr/bin/java'
    DEFAULT_ANUBIS_DIR  = '.'
    #DEFAULT_ANUBIS_JAR  = '/media/storage/code/anubis_workspace/Anubis/target/Anubis-1.1.0-jar-with-dependencies.jar'
    
    
    def prepare_run(self,info,log):
        """
        See interface
        """
        def get(param, default):
            if param not in info:
                info[param] = default
            return info[param]
            
        def require(param):
            if param not in info:
                raise AnubisException('did not find the required %s key' % param)
            return info[param]
            
        def fatal(mess):
            log.fatal(mess)
            print mess
            return ('', info)
                
        
        try:
            cmd = get(self.JVM, self.DEFAULT_JVM)
            cmd += ' -Xmx%s -jar ' % get(self.MAX_HEAP_SIZE, '1g')
            
            if self.VERSION in info:
                cmd += "anubis-%s.jar " % info[self.VERSION]
            else:
                try:
                    anubisCmd = cmd + self.DEFAULT_ANUBIS_DIR + "/anubis.jar"
                    p = subprocess.Popen(shlex.split(anubisCmd), stdout=subprocess.PIPE)
                    output = p.communicate()[0]
                    m = re.search('(?<=anubis-)[^ ]*(?=.jar)', output)
                    if m != None:
                        info[self.VERSION] = m.group(0)
                        cmd += "%s/anubis.jar " % (self.DEFAULT_ANUBIS_DIR)
                    else:
                        return fatal('could not extract anubis version from %s/anubis.jar output' % self.DEFAULT_ANUBIS_DIR)
                except:
                    return fatal('could not run %s/anubis.jar' % cmd + self.DEFAULT_ANUBIS_DIR)
                    


            cmd += "--null-dist=%i "            % int(get(self.NULL_DIST_SIZE, 1000))
            cmd += "--trans-limit=%i "          % int(get(self.MAX_NUM_TRANSITIONS, 6))
            cmd += "--single-answer=%s "        % get(self.SINGLE_ANSWER, "true")
            cmd += "--p-value-tolerance=%f "    % float(get(self.P_VALUE_TOLERANCE, 0.01))
            cmd += '%s ' % require( self.TRAML)
            cmd += "%f " % float(get(     self.PEAK_MIN_WIDTH, 0.1))
            cmd += '%s ' % require( self.OUTPUT_RESULT_FILE)
            cmd += '%s'  % require( self.MZML)
            
            return (cmd, info)
            
        except AnubisException, ae:
            return fatal(ae.mess)
    
    
    
    def set_args(self,log,args_handler):
        """
        See interface
        """        
        args_handler.add_app_args(log, self.NULL_DIST_SIZE, 
            'size of null distrubution for each chromatogram ( > 0, default: 1000)')
            
        args_handler.add_app_args(log, self.MAX_NUM_TRANSITIONS, 
            'limit on the number of transitions used ( > 2, default: 6)')
            
        args_handler.add_app_args(log, self.SINGLE_ANSWER, 
            'report only the best peak per chromatogram (largest within p-value-tolerance of best),'+
            ' instead of every peak within tolerance (false|true, default: true)')
            
        args_handler.add_app_args(log, self.P_VALUE_TOLERANCE, 
            'p-value tolerance where peaks are considered equal (1.0 >= x >= 0.0, default: 0.01)')
            
        args_handler.add_app_args(log, self.PEAK_MIN_WIDTH, 
            'minimum expected peak width in minutes ( > 0.0, default: 0.1)')
            
        args_handler.add_app_args(log, self.TRAML, 
            'traml file with reference transition intensities')
            
        args_handler.add_app_args(log, self.VERSION, 
            'anubis version to use (default: version of anubis.jar)')
            
        args_handler.add_app_args(log, self.JVM, 
            'the jvm to use (default: /usr/bin/java')
            
        args_handler.add_app_args(log, self.MAX_HEAP_SIZE, 
            'jvm max heap size 124m = 124 Mb, 1g = 1 Gb (default: 1g)')
            
        args_handler.add_app_args(log, self.OUTPUT_RESULT_FILE, 
            'the anubis result file')
            
        args_handler.add_app_args(log, self.MZML, 
            'the MzML file to analyze')
            
        return args_handler
    
    
    
    def validate_run(self,info,log,run_code, out_stream, err_stream):
        """
        See interface
        """
        if run_code != 0:
            exit_code = run_code
        else:
            try:
                f = open(info[self.OUTPUT_RESULT_FILE], 'r')
                f.close()
                exit_code = 0
            except:
                log.error('No output file was created. check key [%s]' % self.OUTPUT_RESULT_FILE)
                exit_code = 1
                
        return (exit_code, info)
