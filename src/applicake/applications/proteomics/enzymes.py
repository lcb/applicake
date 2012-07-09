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

    _applications = ['Xtandem','Omssa','Myrimatch','Mascot','InteractParser']

    _enzymes={
           'Trypsin':{
                                  _applications[0]: '[RK]{P}',
                                  _applications[1]: '0',
                                  _applications[2]: 'Trypsin/P:2',  #The number after the ':' is the number of MinTerminiCleavages
                                  _applications[3]: 'Trypsin',
                                  _applications[4]: 'Trypsin'
               
                                  },
           'Semi-Tryptic':{
                            _applications[0]: '[RK]{P}:2', #does not exist and therefore has to be parsed in xtandem class
                            _applications[1]: '16',
                            _applications[2]: 'Trypsin/P:1',
                            _applications[3]: 'semiTrypsin',
                            _applications[4]: 'semiTrypsin',
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
            assert search_engine in self._applications
            return self._enzymes[name][search_engine]
        except:
            self.log.fatal('either name [%s] not found [%s] or search engine [%s] is not supported [%s]' % (name,self._enzymes.keys(),search_engine,self._applications)) 
            sys.exit(1)
            
    def get_keys(self):
        '''
        Return all available enzymes.
        '''
        return self._enzymes.keys()            