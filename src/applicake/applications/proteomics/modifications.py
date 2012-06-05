'''
Created on Jun 5, 2012

@author: quandtan
'''

import sys
from applicake.framework.logger import Logger
from unittest.case import TestCase

class ModificationDb(object):
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
        try:
            assert self._mods.has_key(name)
            assert search_engine in self._search_engines
            return self._mods[name][search_engine]
        except:
            self.log.fatal('either name [%s] not found [%s] or search engine [%s] is not supported [%s]' % (name,self._mods.keys(),search_engine,self._search_engines)) 
            sys.exit(1)
        
    