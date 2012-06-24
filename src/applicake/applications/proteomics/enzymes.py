'''
Created on Jun 15, 2012

@author: quandtan
'''

import sys
from applicake.framework.logger import Logger

class EnzymeDb(object):
    '''
    Access to enzymes
    '''

    _search_engines = ['Xtandem','Omssa','Myrimatch']

    _enzymes={
           'Trypsin':{
                                  _search_engines[0]: '[RK]{P}',
                                  _search_engines[1]: '0',
                                  _search_engines[2]: 'Trypsin/P:2'  #The number after the ':' is the number of MinTerminiCleavages
             
                                  },
           'Semi-Tryptic':{
                            _search_engines[0]: '[RK]{P}:2', #does not exist and therefore has to be parsed in xtandem class
                            _search_engines[1]: '16',
                            _search_engines[2]: 'Trypsin/P:1'   
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
        Return the program specific enzyme.
        """
        try:
            assert self._enzymes.has_key(name)
            assert search_engine in self._search_engines
            return self._enzymes[name][search_engine]
        except:
            self.log.fatal('either name [%s] not found [%s] or search engine [%s] is not supported [%s]' % (name,self._enzymes.keys(),search_engine,self._search_engines)) 
            sys.exit(1)
            
    def get_keys(self):
        '''
        Return all available enzymes.
        '''
        return self._enzymes.keys()            