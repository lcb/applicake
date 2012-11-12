'''
Created on Oct 24, 2012

@author: lorenz
'''
from applicake.utils.dictutils import DictUtils
from applicake.applications.commons.generator import Generator
from applicake.framework.informationhandler import BasicInformationHandler

class WindowGenerator(Generator):
    """
	Generator using SUBFILE_IDX as index for enumeration. Useful for 3rd layer when FILE_IDX and PARAM_IDX are already used.
	(Used in openswath windowgenerator)
	"""
    def main(self,info,log):
        basedic = info.copy()        
        #check if value DATASE_CODE is defined as list
        remove_keys = [self.COPY_TO_WD,self.NAME]        
        for key in remove_keys:
            try:
                del basedic[key]
                log.debug('removed key [%s] from work copy' % key)
            except:
                log.debug('work copy did not have key [%s]' % key)            

        param_dicts = DictUtils.get_product_dicts(basedic, log, escape_keys=[],idx_key='SUBFILE_IDX')
        # write ini files
        self.write_files(info,log,param_dicts)
            
        return (0,info)   
    
    def set_args(self,log,args_handler):
        """
        See interface
        """             
        args_handler.add_app_args(log, "GENERATORS", 'Basename of generated inis', action='append')       
        return args_handler

