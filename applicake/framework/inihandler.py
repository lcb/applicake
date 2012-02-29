'''
Created on Feb 29, 2012

@author: quandtan
'''

class IniHandler(object):
    
    def __init__(self,input_filename,output_filename=None,lock=False):
        self.input_filename = input_filename 
        if output_filename is None:       
            self.output_filename = input_filename
        else:
            self.output_filename = output_filename
        self._lock = lock
        
    def add_to_ini(self,dictionary):
        config = self.read_ini()
        config.update(dictionary)
        self.write_ini(config)               
        
    def read_ini(self): 
        'Read file in windows ini format and returns a dictionary like object (ConfigObj)'
        if not self._lock:
            return ConfigObj(self.input_filename)
        else:
            locker = FileLocker()
            file = open(self.input_filename,'r')        
            locker.lock(file,locker.LOCK_EX)
            config = ConfigObj(self.input_filename)
            locker.unlock(file)       
            return config
               
    def update_ini(self,dictionary):
        'Updates file in windows ini format and returns the updated dictionary like object (ConfigObj)'
        config = self.read_ini()
        for k,v in dictionary.items():
            config[k]=v
        self.write_ini(config)   
        return config 
            
    
    def write_ini(self,dictionary):
        'Write file in windows ini format'
        config = ConfigObj(dictionary)
        config.filename = self.output_filename
        # need to set input pointer to output pointer that read_ini() always gets the latest config
        self.input_filename = self.output_filename
        if not self._lock:
            config.write()
        else:        
            locker = FileLocker()
            file = open(self.output_filename,'r')
            locker.lock(file,locker.LOCK_EX)
            config.write()
            locker.unlock(file)
            
    def write_ini_value_product(self,config=None, use_subdir=True, fname=None, sep='_', index_key=None,fileidx=0):
        '''Takes an ini file as input and generates a new ini file for each value combination.
        The startidx allows to set a start index. this number is incrementally increased.
        The method returns a tuple with the names of the files created and the last index used.
        '''
        output_filenames = []
        if config is None:
            config = self.read_ini()
        keys = config.keys()
        values = config.values()
        elements = Utilities().get_list_product(values)
        if fname == None:
            fname = self.output_filename
        for idx,element in enumerate(elements): 
            # idx = fileidx + idx
            dictionary = None
            if use_subdir:
                dir = os.path.dirname(fname)               
                sub_dir = os.path.join(dir,str(idx))
                os.mkdir(sub_dir)
                self.output_filename=os.path.join(sub_dir,os.path.basename(fname))
                dictionary = dict(zip(keys, element))
                dictionary['DIR'] = sub_dir
            else:                           
                self.output_filename= ''.join((fname,sep,str(fileidx)))                
                fileidx +=1    
                dictionary = dict(zip(keys, element))
                # if no sub dir is generated, the index key can be used to generate a unique path later on
            if index_key is not None:
                dictionary[index_key]=idx
            self.write_ini(dictionary)
            output_filenames.append(self.output_filename)  
            
        return output_filenames,fileidx
    
    
    def write_ini_value_product_continuesidx(self,config=None, use_subdir=True, sep='_', index_key=None):
        'Takes an ini file as input and generates a new ini file for each value combination'
        output_filenames = []
        if config is None:
            config = self.read_ini()
        keys = config.keys()
        values = config.values()
        elements = Utilities().get_list_product(values)
        orig_output_filename = self.output_filename
        for idx,element in enumerate(elements): 
            
            dictionary = None
            if use_subdir:
                dir = os.path.dirname(orig_output_filename)               
                sub_dir = os.path.join(dir,str(idx))
                os.mkdir(sub_dir)
                self.output_filename=os.path.join(sub_dir,os.path.basename(orig_output_filename))
                dictionary = dict(zip(keys, element))
                dictionary['DIR'] = sub_dir
            else:                           
                self.output_filename= ''.join((orig_output_filename,sep,str(idx)))    
                dictionary = dict(zip(keys, element))
                # if no sub dir is generated, the index key can be used to generate a unique path later on
            if index_key is not None:
                dictionary[index_key]=idx
            self.write_ini(dictionary)
            output_filenames.append(self.output_filename)  
        return output_filenames    
