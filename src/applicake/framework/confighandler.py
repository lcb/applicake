'''
Created on Feb 29, 2012

@author: quandtan
'''

import os
from applicake.utils.fileutils import FileLocker
from configobj import ConfigObj
from string import Template 


class ConfigHandler(object): 
    """
    Handler for Config files in ini format
    """

    def __init__(self,lock=False):
        self._lock = lock    
        
    def read(self,path): 
        """
        Read file in windows ini format and returns a dictionary like object (ConfigObj)
        
        Arguments:
        - path: Path to the ini file
        
        Return: The dictionary created from the config file
        """
        if not self._lock:
            return ConfigObj(path)
        else:
            locker = FileLocker()
            fh = open(path,'r')        
            locker.lock(fh,locker.LOCK_EX)
            config = ConfigObj(path)
            locker.unlock(fh)       
            return config
               
    def update(self,dic):
        """
        Updates  in windows ini format and returns the updated dictionary like object (ConfigObj)
        
        Arguments:
        - dic: Dictionary to update
        
        Return: return the updated dictionary
        """
        config = self.read()
        for k,v in dic.items():
            config[k]=v
        self.write(config)   
        return config 
            
    
    def write(self,dic,path):
        """
        Write file in windows ini format
        
        Arguments:
        - dic: Dictionary that should be written to an ini file
        - path: Path to the ini file
        """
        config = ConfigObj(dic)
        config.filename = path
        if not self._lock:
            config.write()
        else:        
            locker = FileLocker()
            fh = open(path,'r')
            locker.lock(file,locker.LOCK_EX)
            config.write()
            locker.unlock(fh)