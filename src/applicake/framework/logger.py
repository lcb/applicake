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

    @staticmethod
    def create(name='logger',level=logging.DEBUG,stream=sys.stderr):
        logger = logging.getLogger(name)
        logger.setLevel(level)                
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        ch = logging.StreamHandler(stream)
        ch.setFormatter(formatter)
        logger.addHandler(ch)   
        return logger             
