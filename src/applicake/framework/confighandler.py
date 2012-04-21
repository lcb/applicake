'''
Created on Feb 29, 2012

@author: quandtan
'''


from applicake.utils.dictutils import DictUtils
from applicake.utils.fileutils import FileLocker
from applicake.utils.fileutils import FileUtils
from configobj import ConfigObj
from string import Template 


class ConfigHandler(object): 
    """
    Handler for Config files in ini format
    """

    def __init__(self,lock=False):
        self._lock = lock 
        
    def get_config(self, input_files):
        success = False
        msg = []
        config = {}
        for fin in input_files:
            valid, msg_valid = FileUtils.is_valid_file(self, fin)
            if not valid:
                msg.append(msg_valid)
                msg = '\n'.join(msg)
                return (success,msg,config)
            else:
                msg.append('file [%s] is valid' % fin)
                new_config = ConfigHandler().read(fin)
                msg.append('created dictionary from file content')
                config = DictUtils.merge(config, new_config, priority='flatten_sequence')
                msg.append('merge content with content from previous files')     
        success = True 
        msg = '\n'.join(msg) 
        return success,msg,config           
        
    def read(self,log,path): 
        """
        Read file in windows ini format and returns a dictionary like object (ConfigObj)
        
        @type log: Logger
        @param log: Logger object to write log messages 
        @type path: string
        @param path: Path to the ini file
        
        @rtype: dict
        @return: The dictionary created from the config file
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