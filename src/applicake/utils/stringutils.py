'''
Created on Jun 20, 2012

@author: quandtan
'''

import random
import string

class StringUtils(object):
    '''
    Utility class for strings
    '''

    @staticmethod
    def get_random(length):
        """
        Generate a random string.
        
        
        @param length: Length of the random string.
        @type length: int
        
        @rtype: string
        @return: A random string
        """
        char_set = string.ascii_uppercase + string.digits
        return ''.join(random.sample(char_set,length))
