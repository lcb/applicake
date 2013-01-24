'''
Created on Sep 29, 2012

@author: quandtan
'''

import os
import sys
from applicake.framework.interfaces import IWrapper

class LibraryCreator(IWrapper):
    '''
    Wrapper for SpectraST in library creation mode.
    '''

    _result_file = ''
    _default_prefix = 'spectrast'

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._result_file1 = '%s.splib' % base # result produced by the application
        self._result_file2 = '%s.sptxt' % base # result produced by the application


    def get_suffix(self,info,log):
        """
        add command line arguments specific to the library creation step.
        """
        raise NotImplementedError("get_suffix() is not implemented") 

    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def prepare_run(self,info,log):
        """
        See interface.

        - Define path to result file (depending on work directory)
        - If there is a result file, it is added with a specific key to the info object.
        """
        # needs to run as first because of the possible overwriting of key values.
        wd = info[self.WORKDIR]
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        # need to make old values accessible if existing
        self._orig_splib = None
        self.orig_sptxt  = None
        if info.has_key(self.SPLIB):
            self._orig_splib = info[self.SPLIB]
        if info.has_key(self.SPTXT):
            self._orig_sptxt = info[self.SPTXT]                
        self._result_file1 = os.path.join(wd,self._result_file1)
        info[self.SPLIB] = self._result_file1
        self._result_file2 = os.path.join(wd,self._result_file2)
        info[self.SPTXT] = self._result_file2
        prefix,info = self.get_prefix(info,log)
        suffix = self.get_suffix(info, log)
        command = '%s -V %s ' % (prefix,suffix)
        
        return command,info

    def set_args(self,log,args_handler):
        """
        See super class.
        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory')  
        #args_handler.add_app_args(log, '', '')
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        """
        if 0 != run_code:
            return run_code,info
        #out_stream.seek(0)
        #err_stream.seek(0)
        return 0,info

class RawLibrary(LibraryCreator):
    '''
    Create a SpectraST raw library
    '''
    def get_suffix(self,info,log):
        if len(info[self.PEPXMLS]) >1:
            log.fatal('found > 1 pepxml files [%s] in [%s].' % (len(info[self.PEPXMLS]),info[self.PEPXMLS]))
            sys.exit(1)           
        #have to symlink the pepxml and mzxml files first into a single directory
        root = os.path.splitext(self._result_file1)[0]
        symlink_files = info[self.PEPXMLS] + info[self.MZXML] 
        for i,f in enumerate(symlink_files):
            dest = os.path.join(os.path.dirname(self._result_file1),os.path.basename(f))
            log.debug('create symlink [%s] -> [%s]' % (f,dest))
            os.symlink(f, dest)
            symlink_files[i] = dest     
                                  
        return '-cP%s -cN%s %s ' % (info[self.PROBABILITY],root,symlink_files[0])

    
    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler = super(RawLibrary, self).set_args(log,args_handler)
        args_handler.add_app_args(log, self.PEPXMLS, 'List of pepXML files',action='append')
        args_handler.add_app_args(log, self.MZXML, 'Peak list file in mzXML format',action='append')
        args_handler.add_app_args(log, self.PROBABILITY, 'Probability cutoff ') 
        return args_handler

class NoDecoyLibrary(LibraryCreator):
    '''
    Remove Decoy entries from a SpectraST library.
    ''' 
    def get_suffix(self,info,log):
        root = os.path.splitext(self._result_file1)[0] 
        return "-cf'Protein !~ REV_  &  Protein !~ DECOY_' -cN%s %s" % (root,self._orig_splib)

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler = super(NoDecoyLibrary, self).set_args(log,args_handler)
        args_handler.add_app_args(log, self.SPLIB, 'Spectrast library in .splib format')
        return args_handler  

class ConsensusLibrary(LibraryCreator):
    '''
    Create a consensus library from a raw SpectraST raw library.
    '''
    def get_suffix(self,info,log):
        root = os.path.splitext(self._result_file1)[0] 
        return "-cAC -cN%s %s" % (root,self._orig_splib)

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler = super(ConsensusLibrary, self).set_args(log,args_handler)
        args_handler.add_app_args(log, self.SPLIB, 'Spectrast library in .splib format')
        return args_handler

class CreateTxtLibrary(LibraryCreator):
    '''
    Convert a SpectraST library in binary format into txt format.
    '''
    def get_suffix(self,info,log):
        root = os.path.splitext(self._result_file1)[0] 
        return "-c_BIN! -cN%s %s" % (root,self._orig_splib)

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler = super(CreateTxtLibrary, self).set_args(log,args_handler)
        args_handler.add_app_args(log, self.SPLIB, 'Spectrast library in .splib format')
        return args_handler
    
class CreateBinLibrary(LibraryCreator):
    '''
    Convert a SpectraST library in txt format into binary format.
    '''
    def get_suffix(self,info,log):
        root = os.path.splitext(self._result_file1)[0] 
        return "-c_BIN -cN%s %s" % (root,self._orig_splib)

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler = super(CreateBinLibrary, self).set_args(log,args_handler)
        args_handler.add_app_args(log, self.SPLIB, 'Spectrast library in .splib format')
        return args_handler


########################################
class RawLibraryNodecoy(LibraryCreator):
    def get_suffix(self,info,log):
        if len(info[self.PEPXMLS]) >1:
            log.fatal('found > 1 pepxml files [%s] in [%s].' % (len(info[self.PEPXMLS]),info[self.PEPXMLS]))
            sys.exit(1)           
        #have to symlink the pepxml and mzxml files first into a single directory
        root = os.path.splitext(self._result_file1)[0]
        symlink_files = info[self.PEPXMLS] + info[self.MZXML] 
        for i,f in enumerate(symlink_files):
            dest = os.path.join(os.path.dirname(self._result_file1),os.path.basename(f))
            log.debug('create symlink [%s] -> [%s]' % (f,dest))
            os.symlink(f, dest)
            symlink_files[i] = dest  
        
        if not info.has_key(self.PROBABILITY):
            log.info("No probability given, trying to get probability from FDR")
            info[self.PROBABILITY] = self.getiProbability(log, info)
        
        root = os.path.join(info['LIBDIR'],os.path.basename(self._result_file1)[0])                  
        return '-cP%s -cN%s %s ' % (info[self.PROBABILITY],root,symlink_files[0])
    
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
        args_handler = super(RawLibrary, self).set_args(log,args_handler)
        args_handler.add_app_args(log, self.PEPXMLS, 'List of pepXML files',action='append')
        args_handler.add_app_args(log, self.MZXML, 'Peak list file in mzXML format',action='append')
        args_handler.add_app_args(log, self.PROBABILITY, 'Probability cutoff value that has to be matched') 
        args_handler.add_app_args(log, self.FDR, 'FDR cutoff (if no probability given)') 
        args_handler.add_app_args(log, 'LIBDIR', 'Folder to put output libraries')
        return args_handler


    
class RTLibrary(LibraryCreator):
    '''
    Create a consensus library from a raw SpectraST raw library.
    '''
    def get_suffix(self,info,log):
        root = os.path.join(info['LIBDIR'],os.path.basename(self._result_file1)[0]) 
        return "-cf'Protein !~ iRT & ' -cN%s %s" % (root,self._orig_splib)

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler = super(RTLibrary, self).set_args(log,args_handler)
        args_handler.add_app_args(log, self.SPLIB, 'Spectrast library in .splib format')
        args_handler.add_app_args(log, 'LIBDIR', 'Folder to put output libraries')
        
        return args_handler