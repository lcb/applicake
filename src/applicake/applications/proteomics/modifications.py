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

    _applications = ['Xtandem','Omssa','Myrimatch','Openms']

    _mods={
           'Carbamidomethyl (C)':{
                                  _applications[0]: '57.021464@C',
                                  _applications[1]: '3',
                                  _applications[2]: 'C 57.021464',
                                  _applications[3]: '<LISTITEM value="Carbamidomethyl (C)"/>'
            
                                  },
           'Oxidation (M)':{
                            _applications[0]: '15.994915@M',
                            _applications[1]: '1',
                            _applications[2]: 'M 15.995',
                            _applications[3]: '<LISTITEM value="Oxidation (M)"/>'
                            },
           'Phospho (STY)':{
                            _applications[0]: '79.966331@S,79.966331@T,79.966331@Y',
                            _applications[1]: '6,7,8,132,133',
                            _applications[2]: '[STY] 79.966',
                            _applications[3]: '<LISTITEM value="Phospho (STY)"/>'
                            },
           '13C(6)15(N)(2) (K)':{
                            _applications[0]: '8.014199@K',
                            _applications[1]: '181',
                            _applications[2]: 'K 8.014199',
                            _applications[3]: '<LISTITEM value="13C(6)15(N)(2) (K)"/>'                          
                            },
           '13C(6)15(N)(4) (R)':{
                            _applications[0]: '10.008269@R',
                            _applications[1]: '137',
                            _applications[2]: 'R 10.008269',
                            _applications[3]: '<LISTITEM value="13C(6)15(N)(4) (R)"/>'
                            },
           'Biotin (K)' : {
                           _applications[0]: '226.077598@K',
                           _applications[1]: '125',
                           _applications[2]: 'K 226.077598',
                           _applications[3]: '<LISTITEM value="Biotin (K)"/>'
                           },
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
        if name == None or name == "":
            self.log.info("No modification used")
            return ''
        try:
            name = name.trim()
            assert self._mods.has_key(name)
            assert search_engine in self._applications
            return self._mods[name][search_engine]
        except:
            self.log.fatal('either name [%s] not found [%s] or search engine [%s] is not supported [%s]' % (name,self._mods.keys(),search_engine,self._applications)) 
            sys.exit(1)
            
    def get_keys(self):
        """
        Return all available modifications.
        """
        return self._mods.keys()
        
    