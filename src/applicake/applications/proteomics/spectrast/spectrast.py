'''
Created on Sep 29, 2012

@author: loblum
'''

import os
from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils

class RawlibNodecoy(IWrapper):
    """
        Create raw text library without DECOYS_ from pepxml 
    """
    def prepare_run(self,info,log):
        #have to symlink the pepxml and mzxml files first into a single directory
        symlink_files = []
        if isinstance(info[self.PEPXMLS], list):
            raise Exception('found > 1 pepxml files [%s] in [%s].' % (len(info[self.PEPXMLS]),info[self.PEPXMLS])) 
        else:
            symlink_files.append(info[self.PEPXMLS])
        
        if isinstance(info[self.MZXML], list):
            symlink_files.extend(info[self.MZXML])  
        else:
            symlink_files.append(info[self.MZXML])

        for i,f in enumerate(symlink_files):
            dest = os.path.join(info[self.WORKDIR],os.path.basename(f))
            log.debug('create symlink [%s] -> [%s]' % (f,dest))
            os.symlink(f, dest)
            symlink_files[i] = dest  
        
        if not info.has_key(self.PROBABILITY):
            log.info("No probability given, trying to get probability from FDR")
            info[self.PROBABILITY] = self.getiProbability(log, info)
        
        root = os.path.join(info[self.WORKDIR],'RawlibNodecoy')
        self._result_file = info[self.SPLIB] = root + '.splib'
        command = 'spectrast -c_BIN! -cP%s -cN%s %s' % (info[self.PROBABILITY],root,symlink_files[0])      
        return command,info
    
    def getiProbability(self,log,info):
        minprob = ''
        for line in open(info['PEPXMLS']):
            if line.startswith('<error_point error="%s' % info['FDR']):
                minprob = line.split(" ")[2].split("=")[1].replace('"','')
                break
            
        if minprob != '':
            log.info("Found minprob %s for FDR %s" % (minprob,info['FDR']) ) 
        else:
            log.fatal("error point for FDR %s not found" % info['FDR'])
            raise Exception("FDR not found")
        return minprob
    
    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler.add_app_args(log, self.PEPXMLS, 'List of pepXML files',action='append')
        args_handler.add_app_args(log, self.MZXML, 'Peak list file in mzXML format',action='append')
        
        args_handler.add_app_args(log, self.PROBABILITY, 'Probability cutoff value that has to be matched') 
        args_handler.add_app_args(log, self.FDR, 'FDR cutoff (if no probability given)') 
                
        args_handler.add_app_args(log, 'LIBOUTBASE', 'Folder to put output libraries')
        args_handler.add_app_args(log, 'PARAM_IDX', 'Parameter index to distinguish')       
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        """
        if 0 != run_code:
            return run_code,info
        
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' % self._result_file)
            return 1,info
        
        return 0,info
    
class RTcalibNoirt(IWrapper):
    '''
        Filter out iRT peptides from RT calibrated spectral library
    '''
    def prepare_run(self,info,log):
        self._orig_splib = info[self.SPLIB]
        
        root = os.path.join(info[self.WORKDIR],'RTcalibNoirt')
        self._result_file = info[self.SPLIB] = root + '.splib'             
        return "spectrast -c_BIN! -cf'Protein !~ iRT & ' -cN%s %s" % (root,self._orig_splib),info

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler.add_app_args(log, self.SPLIB, 'Spectrast library in .splib format')
        
        args_handler.add_app_args(log, 'LIBOUTBASE', 'Basename (folder + filenamebase) for output libraries')
        args_handler.add_app_args(log, 'PARAM_IDX', 'Parameter index to distinguish')           
        return args_handler
    
    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        """
        if 0 != run_code:
            return run_code,info
        
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' % self._result_file)
            return 1,info
        
        return 0,info
