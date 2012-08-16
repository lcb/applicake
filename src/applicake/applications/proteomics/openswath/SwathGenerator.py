
from applicake.utils.dictutils import DictUtils
from applicake.applications.commons.generator import Generator
import os

class SwathGenerator(Generator):
    """
    Generator that rely on the existence of a specific dataset-code key that is retrieved from an OpenBIS instance.
    
    The generator splits the input file by the all possible parameter combinations and then by all defined dataset-codes.
    """
    def main(self,info,log):
        """
        Generate the cartesian product of all values from info and writes them to files. 
        
        There is a distinction between dataset codes and parameters. For every parameter combination
        a new key [%s] is added. Dataset combinations are indexed using another key [%s]. 
        
        @precondition: 'info' object has to contain key [%s]
        @type info: see super class
        @param info: see super class
        @type log: see super class
        @param log: see super class 
        """ % (self.PARAM_IDX,self.DATASET_CODE,self.DATASET_CODE)
        
        # prepare a basedic to produced input files for inner workflow
        files = os.listdir(info["MZMLGZ"])
        mzmlgzfiles = []
        for file in files:
            if str(file).endswith("mzML.gz"):
                mzmlgzfiles.append(file)
        log.debug('create work copy of "info"')   
        basedic = info.copy()        
        #check if value DATASE_CODE is defined as list
        remove_keys = [self.COPY_TO_WD,self.NAME]        
        for key in remove_keys:
            try:
                del basedic[key]
                log.debug('removed key [%s] from work copy' % key)
            except:
                log.debug('work copy did not have key [%s]' % key)            

        
        # prepare first the product of a parameter combinations
        escape_keys = ["MZMLGZ"]
        param_dicts = DictUtils.get_product_dicts(basedic, log, escape_keys,idx_key=self.PARAM_IDX)
        # write ini files
        self.write_files(info,log,param_dicts)
        return (0,info)   
    
    def set_args(self,log,args_handler):
        """
        See interface
        """        
        args_handler.add_app_args(log, "MZMLGZ", 'Files which are created by this application', action='append')       
        return args_handler       
