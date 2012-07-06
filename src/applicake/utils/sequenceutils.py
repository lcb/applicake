'''
Created on Mar 31, 2012

@author: quandtan
'''
import itertools
import sys

class SequenceUtils(object):
    """
    Utilities for handling sequences such as lists, and tuples
    """
    
    @staticmethod
    def findall(list,filter):
        """
        Return all elements of a list that match the filter.
        """
        idxs = SequenceUtils.get_indices(list, filter)
        return [list[idx] for idx in idxs]

    @staticmethod
    def get_flatten_sequence(log,sequence):
        """  
        Returns a single, flat list which contains all elements retrieved
        from the sequence and all recursively contained sub-sequences
        (iterables).
        
        """    
        seq = []
        for e in sequence:
            if hasattr(e, "__iter__") and not isinstance(e, basestring):
                # empty sequences like [] are not considered
                if len(e)>0:
                    seq.extend(SequenceUtils.get_flatten_sequence(log,e))
            else:
                seq.append(e)
        if seq == []:
            log.fatal('no sequence created')
            sys.exit(1)
        return seq 

    @staticmethod
    def get_indices(list, lambda_filter):
        """
        Return a list of indices for all matches.
        
        @param list: List to search
        @type list: list
        @param lambda_filter: lambda filter e.g. lambda x: x>99 
        
        @return: List of indices that match the criteria
        @rtype: list  
        """
        i=0
        indices = []
        while(True):
            try:
                # next value in list passing the test
                nextvalue = filter(lambda_filter, list[i:])[0]
    
                # add index of this value in the index list,
                # by searching the value in L[i:] 
                indices.append(list.index(nextvalue, i))
    
                # iterate i, that is the next index from where to search
                i=indices[-1]+1
            #when there is no further "good value", filter returns [],
            # hence there is an out of range exeption
            except IndexError:
                return indices    
    
    @staticmethod
    def get_list_product(log,list_of_lists):
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
        if l == []:
            log.fatal('no list product was produced.')
            sys.exit(1)    
        return l 

    @staticmethod
    def list2string(dic,keys,escape_str):
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
    
    @staticmethod        
    def string2list(dic,keys,split_str):
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
    
    @staticmethod
    def unify(seq, idfun=None, reduce=False):
        '''
        Remove duplicates from list
        
        @type seq: list
        @param seq: List to unify
        @type reduce: boolean
        @param reduce: If true, a list with a single element is reduced to the element itself
        ''' 
        # order preserving
        if idfun is None:
            def idfun(x): return x
        seen = {}
        result = []
        for item in seq:
            marker = idfun(item)
            # in old Python versions:
            # if seen.has_key(marker)
            # but in new ones:
            if marker in seen: continue
            seen[marker] = 1
            result.append(item)
        if reduce and len(result)==1:
            result = result[0]
        return result          