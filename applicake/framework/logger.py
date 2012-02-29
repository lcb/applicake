'''
Created on Feb 29, 2012

@author: quandtan
'''

import logging

class Logger(object):
    """
    Initialize a logger
    
    Default settings : logging level = DEBUG, logs are written to the console
    """
    def __init__(self,name='logger',level=logging.DEBUG,file=None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)                
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        if file is None:
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)                
        else:                
            fh = logging.FileHandler(file)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)                     
