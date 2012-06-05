'''
Created on Jun 5, 2012

@author: quandtan
'''

import sys
from applicake.framework.logger import Logger
from unittest.case import TestCase

class ModificationDb(TestCase):
    '''
    Access to post-translational modifications (PTMs).
    '''

    _search_engines = ['Xtandem','omssa']

    _mods={
           'Carbamidomethyl (C)':{
                                  _search_engines[0]: '57.021464@C'           
                                  },
           'Phospho (STY)':{
                            _search_engines[0]: '79.966331@S,79.966331@T,79.966331@Y'
                            }
           }           

#    def __init__(self,log=None):
#        '''
#        Constructor
#        
#        @param param: Logger
#        @type param: applicake.framework.logger.Logger 
#        '''
#        if log is None:
#            self.log = Logger.create(level='DEBUG',name='memory_logger',stream=sys.stderr)
#        else:
#            self.log = log


        
    def get(self,name,search_engine):
        """
        Return 
        """
        self.assertTrue(self._mods.has_key(name),'did not find mod name [%s] in list [%s]' % (name,self._mods.keys()))
        self.assertTrue(search_engine in self._search_engines, 'search engine [%s] is not in list of supported engines [%s]' % (search_engine,self._search_engines))
        return self._mods[name][search_engine]        
        
    