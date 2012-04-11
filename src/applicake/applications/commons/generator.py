'''
Created on Mar 20, 2012

@author: quandtan
'''

import itertools
from applicake.framework.confighandler import ConfigHandler
from applicake.framework.interfaces import IApplication

class Generator(IApplication):
    """
    Generates all possible value combinations from the input file if it contains keys with multiple values.
    The results are stored in files which are named in dependency input file name and the pattern accepted 
    by the applied worklfow manager.
    """
    
    
    def main(self,info,log):
        """
        see super class
        """
        # prepare a basedic to produced input files for inner workflow
        basedic = info.copy()
        del basedic['CREATED_FILES']
        # prepare first the product of a parameter combinations
        escape_keys = ['DATASET_CODE']
        param_dicts = self.get_product_dicts(basedic, log, escape_keys,idx_key='PARAM_IDX')
        log.debug('created [%s] dictionaries based on parameter combinations' % len(param_dicts))
        # prepare combinations based on files
        param_file_dicts = []
        escape_keys = []
        for dic in  param_dicts:            
            file_dicts = self.get_product_dicts(dic, log, escape_keys,idx_key='FILE_IDX')
            param_file_dicts.extend(file_dicts)
        log.debug('created [%s] dictionaries based on parameter and file combinations' % len(param_file_dicts))
        # write ini files
        self.write_ini_files(info,log,param_file_dicts)
        return 0

    def get_list_product(self,list_of_lists):
        """
        Generate a list of product combinations from a list of lists
        
        Arguments:
        - list_of_lists: List of lists from which the product combinations should be created
        
        Return: List with all product combinations
        """
        # itertools.product() fails, if not all elements of the list are also lists.
        for idx, val in enumerate(list_of_lists):  
            if type(val) is not list:                
                list_of_lists[idx] = [val] 
        l = []
        for element in itertools.product(*list_of_lists):
            l.append(element)
        return l
    
    def get_product_dicts(self, dic, log, escape_keys,idx_key):
        """
        Creates the value combinations of a dictionary with multiple values for its keys
        
        Arguments:
        - dic: The dictionary
        - log: Logger object
        - escape_keys: List of keys that should be excluded from the combination generation
        - idx_key: Key to store the combination index
        
        Return: List of dictionaries
        """
        escape_str = ';'
        # escape (list-) value of selected keys
        self.list2string(dic, escape_keys, escape_str)
        keys = dic.keys()
        values = dic.values()
        elements = self.get_list_product(values)
        idx = 0
        product_dicts = []
        for idx, element in enumerate(elements):
            dic = dict(zip(keys, element))
            # revert escaping of selected (list-) values
            self.string2list(dic, escape_keys, escape_str)
            # add to each product dictionary a new key: the index key
            dic[idx_key] = idx
            idx += 1
            product_dicts.append(dic)    
        return product_dicts
    
        
    def list2string(self,dic,keys,escape_str):
        """
        Takes a dictionary and transforms values of keys that are lists into a string.
        This might needed to 'escape' lists that should not be part of a list-product generation
        
        Arguments:
        - dic: Dictionary that contains key-holding lists that should be escaped.
        - keys: List of keys for which their values have to be transformed.
        - escape_str: String used to transform a list to a string. The string should not be ',' as this is used
        to generate list products
        """
        for key in keys:
            val = dic[key]
            dic[key] = escape_str.join(val)
            
    def string2list(self,dic,keys,split_str):
        """
        Takes a dictionary and transforms values of keys that are lists into a string.
        This might needed to 'escape' lists that should not be part of a list-product generation
        
        Arguments:
        - dic: Dictionary that contains key-holding lists that should be escaped.
        - keys: List of keys for which their values have to be transformed.
        - escape_str: String used to split a string and generate a list.
        """
        for key in keys:
            val = dic[key]
            dic[key] = val.split(split_str)
            
    def write_ini_files(self,info,log,dicts):
        """
        Generates ini files from a list of dictionaries
        
        Arguments:
        - info: Dictionary with informaiton about the application. The created output files are added to the key 'CREATED_FILES'
        - dicts: List of dictionaries used to create ini files
        """
        raise NotImplementedError("write_ini_files() is not implemented.") 
        
        
class GuseGenerator(Generator):
    """
    Generator for the GUSE workflow manager.
    It creates output files of the format [INPUTFILENAME].[INDEX]
    """
    
    def write_ini_files(self,info,log,dicts): 
        """
        see super class
        """       
        for idx,dic in enumerate(dicts):
            outfile = "%s.%s" % (info["OUTPUT"],idx) 
            log.debug(outfile)          
            ConfigHandler().write(dic, outfile)
            log.debug('create file [%s]' % outfile)
            info['CREATED_FILES'].append(outfile)