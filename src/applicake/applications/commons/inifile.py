'''
Created on Jun 20, 2012

@author: quandtan
'''
from applicake.framework.interfaces import IApplication
from applicake.utils.sequenceutils import SequenceUtils

class Unifier(IApplication):
    '''
    Unify the values of a ini file
    '''


    def main(self,info,log):
        """
        See interface.
        """
        reduce = info['UNIFIER_REDUCE']
        if isinstance(reduce, list):
            if len(reduce)>1:
                log.error('found ambigious value [%s] for key [%s]'% (reduce,'UNIFIER_REDUCE'))
                return 1,info
            else:
                reduce = reduce[0]
        for key in info.keys():
            print key
            if isinstance(info[key], list):
                info[key] = SequenceUtils.unify(info[key], reduce = reduce)
        return 0,info
        
        
    def set_args(self,log,args_handler):
        """
        See interface.
        """                
        args_handler.add_app_args(log, self.COPY_TO_WD, 'Files which are created by this application', action='append')
        args_handler.add_app_args(log,'UNIFIER_REDUCE',"If set, lists with a single element are reduced to that element.",
                                  action="store_true",default=False)  
        return args_handler