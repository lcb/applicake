"""
Created on Feb 29, 2012

@author: quandtan
"""

import logging
import sys
import random


class Logger(object):
    """
    Initialize a logger
    """

    @staticmethod
    def create(name='logger', level='DEBUG', stream=sys.stderr):
        logger = logging.getLogger(name + str(random.random()))
        logger.setLevel(level)
        ch = logging.StreamHandler(stream)
        if level == 'DEBUG':
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] %(message)s")
        else:
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger
