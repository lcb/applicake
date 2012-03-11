'''
Created on Feb 29, 2012

@author: quandtan
'''

import logging
import sys

class Logger(object):
    """
    Initialize a logger
    
    Default settings : logging level = DEBUG, logs are written to the console
    """

    def __init__(self,name='logger',level=logging.DEBUG,stream=sys.stderr):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)                
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        ch = logging.StreamHandler(stream)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)                
