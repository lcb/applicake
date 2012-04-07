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
    def merge(self, dict_1, dict_2, priority='left'):
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
        
        Return: merged dictionary
        """
        if priority == 'left':     
            return dict(dict_2,**dict_1)
        elif priority == 'right':     
            return dict(dict_1,**dict_2)  
        elif priority == 'flatten_sequence':
            dictionary = dict_1.copy()
            for k,v in dict_2.iteritems():
                if k in dictionary.keys():
                    if dictionary[k] != dict_2[k]:                        
                        sequence = [dictionary[k],dict_2[k]]
                        dictionary[k] = DictUtils.get_flatten_sequence(sequence)
                else:
                    dictionary[k]=v
            return dictionary
        
    @staticmethod
    def remove_none_entries(dictionary):
        """
        Removes key/value pairs where the value is None
        
        Input:
        - dictionary 
        
        Return: Copy of the input dictionary where the None key/values are removed
        """
        copied_dict  = dictionary.copy()
        keys = []
        for k,v in copied_dict.iteritems():
            if v is None:
                keys.append(k)
        for k in keys:
            copied_dict.pop(k)
        return copied_dict        