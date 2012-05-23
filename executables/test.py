'''
Created on May 23, 2012

@author: quandtan
'''
from applicake.utils.dictutils import DictUtils


d1 = {
       'BASEDIR': '/tmp',                   
       'COMMENT': 'hello world',
       'FILE_IDX': 0,
       'JOB_IDX': 0,
       'LOG_LEVEL': 'INFO',
       'OUTPUT': '../../../data/output.ini',
       'PARAM_IDX': 0,
       'STORAGE': 'memory',
#       'SECTION': {'SUB_1':11},
       'LIST': [11]
       }

d2 = {
           'BASEDIR': '/tmp',                   
           'COMMENT': 'hello world',
           'FILE_IDX': 0,
           'JOB_IDX': 0,
           'LOG_LEVEL': 'INFO',
           'OUTPUT': '../../../data/output.ini',
           'PARAM_IDX': 0,
           'STORAGE': 'memory',
#           'SECTION': {'SUB_2':22},
           'LIST': [22,222]
           } 


def unify(seq, idfun=None): 
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
    return result

for key in d2.keys():
    if key in d1.keys():
#        val = d1[key]
#        if isinstance(val, list):
#            val2 = d2[key]
#            if isinstance(val2,list):
#                d1[key] = val + val2
#            else:
#                d1[key] = val.append(val2)
#            
#        else:
#            d1[key] = [val,d2[key]]
        val = [d1[key],d2[key]]
        d1[key] = DictUtils.get_flatten_sequence(val)
        
    else:
        d1[key] = d2[key]
        
print d1

for key in d1.keys():
    val = d1[key]
    if isinstance(val,list):       
        val = unify(val)
        if len(val) == 1:
            d1[key] = val[0]
        else:
            d1[key] = val  
           
print d1     
        