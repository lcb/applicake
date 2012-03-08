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
#    def __init__(self,name='logger',level=logging.DEBUG,file=None):
#        self.logger = logging.getLogger(name)
#        self.logger.setLevel(level)                
#        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
#        if file is None:
#            ch = logging.StreamHandler()
#            ch.setFormatter(formatter)
#            self.logger.addHandler(ch)                
#        else:                
#            fh = logging.FileHandler(file)
#            fh.setFormatter(formatter)
#            self.logger.addHandler(fh)                     


#>>> fin = open("test.log", "a+")
#>>> ch = logging.StreamHandler(fin)
#>>> formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
#>>> ch.setFormatter(formatter)
#>>> logger = logging.getLogger('t')
#>>> logger.setLevel(logging.DEBUG)
#>>> logger.addHandler(ch) 
#>>> logger.debug('testlog')
#>>> logger = logging.getLogger('t')
#>>> logger = logging.getLogger('m')
#>>> logger.setLevel(logging.DEBUG)
#>>> out = cStringIO.StringIO()
#>>> ch = logging.StreamHandler(out)
#>>> ch.setFormatter(formatter)
#>>> logger.addHandler(ch) 
#>>> logger.debug('testlog')
#>>> out
#<cStringIO.StringO object at 0x1004a3c38>
#>>> out.seek(0)
#>>> out.read()
#'2012-03-08 21:53:15,174 - DEBUG - testlog\n'

    def __init__(self,name='logger',level=logging.DEBUG,stream=sys.stderr):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)                
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        ch = logging.StreamHandler(stream)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)                
