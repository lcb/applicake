from applicake.utils.sequenceutils import SequenceUtils
from applicake.utils.dictutils import DictUtils
from applicake.applications.commons.generator import Generator
from applicake.framework.informationhandler import BasicInformationHandler

class SetGenerator(Generator):
    """
    Generator that runs after a collector to split the information by the parameter sets.
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
        """ 
        
        
        if not isinstance(info[self.FILE_IDX],list):
            log.info('value [%s] of key [%s] was no list, converting' % (info[self.FILE_IDX],self.FILE_IDX))
            info[self.FILE_IDX] = [info[self.FILE_IDX]]
			
        #remove SUBfile_idx as it is not longer needed
        basedic = info.copy()
        del basedic['SUBFILE_IDX']        
        file_dicts = []
        if len(SequenceUtils.unify(basedic[self.FILE_IDX], reduce = True)) ==1:                        
            for key in basedic.keys():
                if isinstance(basedic[key], list) and key != self.INPUT:
                    basedic[key] = SequenceUtils.unify(basedic[key], reduce = True)
            file_dicts.append(basedic)            
        else:
            keys = basedic.keys()
            log.debug('number of keys [%s]' % len(keys))
            file_idxs = basedic[self.FILE_IDX]
            # loops of unique list of found parameter idices
            for file_idx in SequenceUtils.unify(file_idxs):
                file_dict = {}
                positions = SequenceUtils.get_indices(file_idxs, lambda x: x == file_idx)
                for key in keys:
                    value = basedic[key]    
                    if not isinstance(value, list):
                        log.info('found value %s is not a list', value)
                        file_dict[key] = value
                    elif len(value) != len(file_idxs):
                        log.info('length of value [%s] does not correspond to length of file indices [%s]. key possibly not coming from input file' % (value,len(file_idxs)))
                        file_dict[key] = SequenceUtils.unify(value,reduce=True)
                    else:                
                        values = [value[pos] for pos in positions]
                        log.info('ADDING ' + str(SequenceUtils.unify(values,reduce=True)) + ' to ' + key)
                        file_dict[key] = SequenceUtils.unify(values,reduce=True)
                log.info('param idx [%s] created dict [%s]' % (file_idx,file_dict))
                file_dicts.append(file_dict)    
        # write ini files
        info = self.write_files(basedic,log,file_dicts)
        return (0,info)           
            
    
    def set_args(self,log,args_handler):
        """
        See interface
        """        
        args_handler.add_app_args(log, self.GENERATOR, 'Base name for generating output files (such as for a parameter sweep)',action='append')
        args_handler.add_app_args(log, self.COPY_TO_WD, 'Files which are created by this application', action='append')       
        return args_handler     
