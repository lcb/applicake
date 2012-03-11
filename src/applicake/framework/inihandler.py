'''
Created on Feb 29, 2012

@author: quandtan
'''

import os
from applicake.framework.utils import FileLocker
from applicake.framework.utils import Utilities
from configobj import ConfigObj
from string import Template 

class IniHandler(dict):
    """
    Handling of configuration files in windows ini format
    """ 
    
    def __init__(self,dict=None,lock=False):
        if dict is None:
            self._config = ConfigObj({})
        else:
            self._config = ConfigObj(dict)
        self._lock = lock
        
    def add(self,dictionary):        
        self._config.update(dictionary)               
        
    def get(self):
        return self._config    
        
    def merge(self, config):
        """
        Merge 2 config files
        
        Value lists are generated for keys that are shared between the config files. 
        If a key value pair does not exist in the original config file, it is added.
        
        Input: Configuration object (dictionary) that should be merged with the existing one.  
        """
        for k,v in config.iteritems():
            if k in self._config.keys():
                if self._config[k] is list:
                    self._config[k].append(v)
                else:
                    self._config[k]=self._config[k],v
            else:
                self._config[k]=[v]

                        
    def read(self,filename): 
        'Read file in windows ini format and returns a dictionary like object (ConfigObj)'
        if not self._lock:
            self._config = ConfigObj(self.input_filename)
        else:
            locker = FileLocker()
            file = open(self.input_filename,'r')        
            locker.lock(file,locker.LOCK_EX)
            self._config = ConfigObj(self.input_filename)
            locker.unlock(file)       

    def update(self,dict):
        'Updates file in windows ini format and returns the updated dictionary like object (ConfigObj)'        
        for k,v in dict.items():
            self._config[k]=v                
    
    def write(self,filename):
        'Write file in windows ini format'
        if not self._lock:
            self._write_config(filename)
        else:        
            locker = FileLocker()
            f = open(filename,'r')
            locker.lock(f,locker.LOCK_EX)
            self._write_config(filename)
            locker.unlock(f)
            
    def _write_config(self,filename):
        c = ConfigObj(self._config)
        c.filename = filename
        c.write()
#            
#    def write_value_product(self,config=None, use_subdir=True, fname=None, sep='_', index_key=None,fileidx=0):
#        '''Takes an ini file as input and generates a new ini file for each value combination.
#        The startidx allows to set a start index. this number is incrementally increased.
#        The method returns a tuple with the names of the files created and the last index used.
#        '''
#        output_filenames = []
#        if config is None:
#            config = self.read()
#        keys = config.keys()
#        values = config.values()
#        elements = Utilities().get_list_product(values)
#        if fname == None:
#            fname = self.output_filename
#        for idx,element in enumerate(elements): 
#            # idx = fileidx + idx
#            dictionary = None
#            if use_subdir:
#                dir = os.path.dirname(fname)               
#                sub_dir = os.path.join(dir,str(idx))
#                os.mkdir(sub_dir)
#                self.output_filename=os.path.join(sub_dir,os.path.basename(fname))
#                dictionary = dict(zip(keys, element))
#                dictionary['DIR'] = sub_dir
#            else:                           
#                self.output_filename= ''.join((fname,sep,str(fileidx)))                
#                fileidx +=1    
#                dictionary = dict(zip(keys, element))
#                # if no sub dir is generated, the index key can be used to generate a unique path later on
#            if index_key is not None:
#                dictionary[index_key]=idx
#            self.write(dictionary)
#            output_filenames.append(self.output_filename)  
#            
#        return output_filenames,fileidx
#    
#    
#    def write_value_product_continuesidx(self,config=None, use_subdir=True, sep='_', index_key=None):
#        'Takes an ini file as input and generates a new ini file for each value combination'
#        output_filenames = []
#        if config is None:
#            config = self.read()
#        keys = config.keys()
#        values = config.values()
#        elements = Utilities().get_list_product(values)
#        orig_output_filename = self.output_filename
#        for idx,element in enumerate(elements): 
#            
#            dictionary = None
#            if use_subdir:
#                dir = os.path.dirname(orig_output_filename)               
#                sub_dir = os.path.join(dir,str(idx))
#                os.mkdir(sub_dir)
#                self.output_filename=os.path.join(sub_dir,os.path.basename(orig_output_filename))
#                dictionary = dict(zip(keys, element))
#                dictionary['DIR'] = sub_dir
#            else:                           
#                self.output_filename= ''.join((orig_output_filename,sep,str(idx)))    
#                dictionary = dict(zip(keys, element))
#                # if no sub dir is generated, the index key can be used to generate a unique path later on
#            if index_key is not None:
#                dictionary[index_key]=idx
#            self.write(dictionary)
#            output_filenames.append(self.output_filename)  
#        return output_filenames    
