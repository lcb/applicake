'''
Created on Mar 20, 2012

@author: quandtan
'''

import os
import itertools
from applicake.framework.confighandler import ConfigHandler
from applicake.framework.interfaces import IApplication

class Generator(IApplication):
    '''
    classdocs
    '''

    def main(self,info,log):
        escape_keys = ['CREATED_FILES','DATASET_CODE'] #'CREATED_FILES' 'DATASET_CODE'
        param_dicts = self.get_product_dicts(info, log, escape_keys,idx_key='PARAM_IDX')
        log.debug('created [%s] dictionaries based on parameter combinations' % len(param_dicts))
        param_file_dicts = []
        escape_keys = ['CREATED_FILES']
        for dic in  param_dicts:            
            file_dicts = self.get_product_dicts(dic, log, escape_keys,idx_key='FILE_IDX')
            param_file_dicts.extend(file_dicts)
        log.debug('created [%s] dictionaries based on parameter and file combinations' % len(param_file_dicts))
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
    
    def get_product_dicts(self, info, log, escape_keys,idx_key):
        """
        """
        escape_str = ';'
        basedict = info.copy()
        # escape (list-) value of selected keys
        self.list2string(basedict, escape_keys, escape_str)
        keys = basedict.keys()
        values = basedict.values()
        elements = self.get_list_product(values)
        idx = 0
        product_dicts = []
        for idx, element in enumerate(elements):
            dic = dict(zip(keys, element))
            # revert escaping of selected (list-) values
            self.string2list(dic, escape_keys, escape_str)
            # add to each product dictionary a new key: the index key
            dic[idx_key] = idx
#            log.debug('index [%s]' % idx)
#            log.debug(dic)
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
    
    def write_ini_files(self,info,log,dicts): 
        """
        see super method
        """       
        for idx,dic in enumerate(dicts):
            outfile = "%s.%s" % (info["OUTPUT"],idx)
#            outfile = os.path.join(info[])  
            log.debug(outfile)          
            ConfigHandler().write(dic, outfile)
            log.debug('create file [%s]' % outfile)
            info['CREATED_FILES'].append(outfile)