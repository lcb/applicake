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
        Examples:
        >>> [1, 2, [3,4], (5,6)]
        [1, 2, [3, 4], (5, 6)]
        >>> get_flatten_sequence([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
        [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""    
        seq = []
        for e in sequence:
            if hasattr(e, "__iter__") and not isinstance(e, basestring):
                seq.extend(SequenceUtils.get_flatten_sequence(e))
            else:
                seq.append(e)
        return seq 