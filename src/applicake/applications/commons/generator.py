'''
Created on Mar 20, 2012

@author: quandtan
'''

import itertools
from applicake.framework.confighandler import ConfigHandler
from applicake.framework.interfaces import IApplication

class BasicGenerator(IApplication):
    """
    Generates all possible value combinations from the input file if it contains keys with multiple values.
    The results are stored in files which are named in dependency input file name and the pattern accepted 
    by the applied worklfow manager.
    """
    
    
    def main(self,info,log):
        """
        Generate the cartesian product of all values from info and writes them to files.  
        
        @type info: see super class
        @param info: see super class
        @type log: see super class
        @param log: see super class 
        """
        # prepare a basedic to produced input files for inner workflow
        basedic = info.copy()
        del basedic[self.created_files_key]
        # prepare first the product of a parameter combinations
        escape_keys = [self.dataset_code_key]
        param_dicts = self.get_product_dicts(basedic, log, escape_keys,idx_key=self.param_idx_key)
        log.debug('created [%s] dictionaries based on parameter combinations' % len(param_dicts))
        # prepare combinations based on files
        param_file_dicts = []
        escape_keys = []
        for dic in  param_dicts:            
            file_dicts = self.get_product_dicts(dic, log, escape_keys,idx_key=self.file_idx_key)
            param_file_dicts.extend(file_dicts)
        log.debug('created [%s] dictionaries based on parameter and file combinations' % len(param_file_dicts))
        # write ini files
        self.write_generator_files(info,log,param_file_dicts)
        return (0,info)

    def get_list_product(self,list_of_lists):
        """
        Generate a list of product combinations from a list of lists.
        
        @type list_of_lists: list of lists
        @param list_of_lists: List of lists from which the product combinations should be created
        
        @return: List with all product combinations
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
        
        @type dic: dict
        @param dic: Dictionary used to generate cartesian products from 
        @type log: Logger
        @param log: Logger object to write log messages 
        @type escape_keys: list 
        @param escape_keys: List of keys that should be excluded from the combination generation
        @type idx_key: string 
        @param idx_key: Key to store the combination index
        
        @return: List of dictionaries
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
        
        @type dic: dict 
        @param dic: Dictionary that contains key-holding lists that should be escaped.
        @type keys: list
        @param keys: List of keys for which their values have to be transformed.
        @type escape_str: string
        @param escape_str: String used to transform a list to a string. The string should not be ',' as this is used
        to generate list products
        """
        for key in keys:
            val = dic[key]
            dic[key] = escape_str.join(val)
            
    def string2list(self,dic,keys,split_str):
        """
        Takes a dictionary and transforms values of keys that are lists into a string.
        This might needed to 'escape' lists that should not be part of a list-product generation
        
        @type dic: dict 
        @param dic: Dictionary that contains key-holding lists that should be escaped.
        @type keys: list
        @param keys: List of keys for which their values have to be transformed.
        @type escape_str: string
        @param escape_str: String used to split a string and generate a list.    
        """
        for key in keys:
            val = dic[key]
            dic[key] = val.split(split_str)
            
    def write_generator_files(self,info,log,dicts):
        """
        Generates ini files from a list of dictionaries
        
        @type info: dict 
        @param info: Dictionary with information about the application. The created output files are added to the key [%s]
        @type dicts: list
        @type dicts: List of dictionaries used to create ini files
        """ % info.created_files_key
        raise NotImplementedError("write_generator_files() is not implemented.") 
        
        
class GuseGenerator(BasicGenerator):
    """
    Basic generator for the gUSE workflow manager.
    
    It creates output files of the format [INPUTFILENAME]_[INDEX]
    """
    
    def write_generator_files(self,info,log,dicts): 
        """
        see super class
        """       
        for idx,dic in enumerate(dicts):
            path = "%s_%s" % (dic[self.output_key],idx) 
            log.debug(path)          
            ConfigHandler().write(dic, path)
            log.debug('create file [%s]' % path)
            info[self.created_files_key].append(path)
            
class PgradeGenerator(BasicGenerator):
    """
    Basic generator for the P-Grade workflow manager.
    
    It creates output files of the format [INPUTFILENAME].[INDEX]
    """
    
    def write_generator_files(self,info,log,dicts): 
        """
        see super class
        """       
        for idx,dic in enumerate(dicts):
            path = "%s.%s" % (dic[self.output_key],idx) 
            log.debug(path)          
            ConfigHandler().write(dic, path)
            log.debug('create file [%s]' % path)
            info[self.created_files_key].append(path)