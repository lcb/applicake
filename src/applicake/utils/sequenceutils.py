'''
Created on Mar 31, 2012

@author: quandtan
'''

class SequenceUtils(object):
    """
    Utilities for handling sequences such as lists, and tuples
    """

    @staticmethod
    def get_flatten_sequence(sequence):
        """get_flatten_sequence(sequence) -> list    
        Returns a single, flat list which contains all elements retrieved
        from the sequence and all recursively contained sub-sequences
        (iterables).
        """    
        seq = []
        for e in sequence:
            if hasattr(e, "__iter__") and not isinstance(e, basestring):
                seq.extend(SequenceUtils.get_flatten_sequence(e))
            else:
                seq.append(e)
        return seq 
    
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