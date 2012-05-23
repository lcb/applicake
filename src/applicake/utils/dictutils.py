'''
Created on Mar 31, 2012

@author: quandtan
'''

from applicake.utils.sequenceutils import SequenceUtils


class DictUtils(SequenceUtils):
    """
    Utilities for handling dictionaries
    """
    
    @staticmethod
    def extract(dic,keys,include=True):
        """
        Extract subset of a dictionary based on a list of keys which are either included or excluded.
        
        @type dic: dict
        @param dic: The original dictionary
        @type keys:list 
        @param keys: : Keys used to create the subset
        @type include: boolean
        @param include: Defines if the list of keys is inclusive or exclusive
        
        @return: Dictionary containing the subset
        """
        if include:        
            return dict((key, dic[key]) for key in keys if key in dic)
        else:
            sub_dic = dic.copy()
            for key in keys:
                if key in sub_dic: del sub_dic[key] 
            return sub_dic
            
    
    @staticmethod  
    def merge(dict_1, dict_2, priority='left'):
        """
        Merging of 2 dictionaries
        
        Arguments:
        - dict_1: first dictionary
        - dict_2: second dictionary
        - priority: priority of the merging
        -- left: First dictionary overwrites existing keys in second dictionary
        -- right: Second dictionary overwrites existing keys in first dictionary
        -- equal: Keys with same values are not changed. 
            Keys with different values are merged into lists where the value of 
            dict_1 is first in the list.
            Keys that only exist in one dictionary are added
        
        @return: merged dictionary
        """
        d1 = dict_1.copy()
        d2 = dict_2.copy()
        if priority == 'left':     
            return dict(d2,**d1)
        elif priority == 'right':     
            return dict(d1,**d2)  
        elif priority == 'flatten_sequence':
            for k,v in d2.iteritems():
                if k in d1.keys():
                    if d1[k] != d2[k]:                        
                        sequence = [d1[k],d2[k]]
                        d1[k] = DictUtils.get_flatten_sequence(sequence)
                else:
                    d1[k]=v
            return d1
        elif priority == 'append':
            for key in d2.keys():
                if key in d1.keys():
                    val = [d1[key],d2[key]]
                    d1[key] = DictUtils.get_flatten_sequence(val)
                else:
                    d1[key] = d2[key] 
            return d1           
            

        
    @staticmethod
    def remove_none_entries(dic):
        """
        Removes key/value pairs where the value is None
        
        @type dic: dict
        @param dic: Dictionary from which the none values should be removed 
        
        @return: Copy of the input dictionary where the None key/values are removed
        """
        copied_dict  = dic.copy()
        keys = []
        for k,v in copied_dict.iteritems():
            if v is None:
                keys.append(k)
        for k in keys:
            copied_dict.pop(k)
        return copied_dict   
    
    @staticmethod
    def sort(dic,by='key'):
        """
        Sort a dictionary.
        
        @type dic: dict
        @param dic: Dictionary to sort
        @type by: string
        @param by: How to sort dictionary (key|value)
        
        @rtype: dict
        @return: The sorted dictionary.  
        """
        d = dic.copy()
        if type == 'key':
            return sorted(d.items(), key=lambda t: t[1])    
        elif type == 'value':
            return sorted(d.items(), key=lambda t: t[0])   
         