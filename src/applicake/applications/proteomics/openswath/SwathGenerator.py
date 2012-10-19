
from applicake.utils.dictutils import DictUtils
from applicake.applications.commons.generator import Generator
import os
import re

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
        files = os.listdir(info["MZMLGZDIR"])
        #http://code.activestate.com/recipes/135435-sort-a-string-using-numeric-order/
        def stringSplitByNumbers(x):
            r = re.compile('(\d+)')
            l = r.split(x)
            return [int(y) if y.isdigit() else y for y in l]
        files = sorted(files, key=stringSplitByNumbers)  

        mzmlgzfiles = []
        for file in files:
            if str(file).endswith("mzML.gz") and not "ms1scan" in str(file):
                mzmlgzfiles.append(os.path.join(info["MZMLGZDIR"],file))
        
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
        basedic["MZMLGZ"] = mzmlgzfiles
        basedic["PARAM_IDX"] = 0
        escape_keys = [] #escape keys are NOT iterated!
    
        #first the 'normal' FILES
        basedic["TRAML"] = basedic["LIBTRAML"]
        basedic["OUTSUFFIX"] = basedic["LIBOUTSUFFIX"]
        param_dicts = DictUtils.get_product_dicts(basedic, log, escape_keys,idx_key=self.FILE_IDX)
        # write ini files
        self.write_files(info,log,param_dicts)
    
        #second the iRT files
        basedic["TRAML"] = basedic["IRTTRAML"]
        basedic["OUTSUFFIX"] = basedic["IRTOUTSUFFIX"]
        basedic["GENERATORS"] = basedic["GENERATORSIRT"]

        param_dicts = DictUtils.get_product_dicts(basedic, log, escape_keys,idx_key=self.FILE_IDX)
        # write ini files
        self.write_files(info,log,param_dicts)
    
        return (0,info)   
    
    def set_args(self,log,args_handler):
        """
        See interface
        """        
        args_handler.add_app_args(log, "MZMLGZDIR", 'Folder with mzmlgz used', action='append')       
        args_handler.add_app_args(log, "GENERATORS", 'Basename of generated inis', action='append')       
        args_handler.add_app_args(log, "GENERATORSIRT", 'Basename of generated inis FOR IRT', action='append')       
        args_handler.add_app_args(log, "TRAML", 'Traml used by chromextract ', action='append')       
        args_handler.add_app_args(log, "IRTTRAML", 'Traml used by chromextractIRT', action='append') 
        args_handler.add_app_args(log, "OUTSUFFIX", 'Suffix used by chromextract', action='append') 
        args_handler.add_app_args(log, "IRTOUTSUFFIX", 'Suffix used by chromextractIRT', action='append')         
        return args_handler
