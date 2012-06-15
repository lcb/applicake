'''
Created on Jun 5, 2012

@author: quandtan
'''

import sys
from applicake.framework.logger import Logger

class ModificationDb(object):
    '''
    Access to post-translational modifications (PTMs).
    '''

    _search_engines = ['Xtandem','Omssa']

    _mods={
           'Carbamidomethyl (C)':{
                                  _search_engines[0]: '57.021464@C',
                                  _search_engines[1]: '3'           
                                  },
           'Oxidation (M)':{
                            _search_engines[0]: '15.994915@M',
                            _search_engines[1]: '1' 
                            },
           'Phospho (STY)':{
                            _search_engines[0]: '79.966331@S,79.966331@T,79.966331@Y',
                            _search_engines[1]: '6,7,8,132,133'
                            },
           '13C(6)15(N)(2) (K)':{
                            _search_engines[0]: '8.014199@K',
                            _search_engines[1]: '181'
                            },
           '13C(6)15(N)(4) (R)':{
                            _search_engines[0]: '10.008269@R',
                            _search_engines[1]: '137'
                            }
           }           

    def __init__(self,log=None):
        '''
        Constructor
        
        @param param: Logger
        @type param: applicake.framework.logger.Logger 
        '''
        if log is None:
            self.log = Logger.create(level='DEBUG',name='memory_logger',stream=sys.stderr)
        else:
            self.log = log


        
    def get(self,name,search_engine):
        """
        Return the program specific modification.
        """
        try:
            assert self._mods.has_key(name)
            assert search_engine in self._search_engines
            return self._mods[name][search_engine]
        except:
            self.log.fatal('either name [%s] not found [%s] or search engine [%s] is not supported [%s]' % (name,self._enzymes.keys(),search_engine,self._search_engines)) 
            sys.exit(1)
            
    def get_keys(self):
        """
        Return all available modifications.
        """
        return self._mods.keys()
        
    