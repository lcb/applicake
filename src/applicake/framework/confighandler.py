'''
Created on Feb 29, 2012

@author: quandtan
'''

import os
from applicake.framework.utils import FileLocker
from applicake.framework.utils import Utilities
from configobj import ConfigObj
from string import Template 


class ConfigHandler(object): 
    
    @staticmethod
    def get_new_dict(self):
        return {}
        
        
    
    def __init__(self,lock=False):
        self._lock = lock
        
#    def add_to_ini(self,dictionary):
#        config = self.read()
#        config.update(dictionary)
#        self.write(config)      
        
        
    def append(self,config_1,config_2):
        """
        Append 
        
        Value lists are generated for keys that are shared between the config files. 
        If a key value pair does not exist in the original config file, it is added.
        
        Input: Configuration object (dictionary) that should be merged with the existing one.  
        """
        for k,v in config_2.iteritems():
            if k in config_1.keys():
                if isinstance(config_1[k],list):
                    config_1[k].append(v)
                else:
                    config_1[k]=[config_1[k],v]
            else:
                config_1[k]=[v]
        return config_1                 
        
    def read(self,filename): 
        'Read file in windows ini format and returns a dictionary like object (ConfigObj)'
        if not self._lock:
            return ConfigObj(filename)
        else:
            locker = FileLocker()
            file = open(filename,'r')        
            locker.lock(file,locker.LOCK_EX)
            config = ConfigObj(filename)
            locker.unlock(file)       
            return config
               
    def update(self,dictionary):
        'Updates file in windows ini format and returns the updated dictionary like object (ConfigObj)'
        config = self.read()
        for k,v in dictionary.items():
            config[k]=v
        self.write(config)   
        return config 
            
    
    def write(self,dictionary,filename):
        'Write file in windows ini format'
        config = ConfigObj(dictionary)
        config.filename = filename
        # need to set input pointer to output pointer that read_ini() always gets the latest config
#        self.input_filename = self.output_filename
        if not self._lock:
            config.write()
        else:        
            locker = FileLocker()
            fh = open(filename,'r')
            locker.lock(file,locker.LOCK_EX)
            config.write()
            locker.unlock(fh)
            
#    def write_ini_value_product(self,config=None, use_subdir=True, fname=None, sep='_', index_key=None,fileidx=0):
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
#    def write_ini_value_product_continuesidx(self,config=None, use_subdir=True, sep='_', index_key=None):
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
