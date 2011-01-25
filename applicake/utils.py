'''
Created on Dec 14, 2010

@author: quandtan
'''

import logging,itertools,os,fcntl,time,random,xml.parsers.expat,sys
#import win32con, win32file, pywintypes,fcntl
from configobj import ConfigObj #easy_install configobj
from string import Template 
 
class Workflow():
    
    def get_jobid(self,dirname):
        'Return a unique job id'
        jobid = 1
        filename = os.path.join(dirname, 'jobid.txt')
        locker = FileLocker()
        if (os.path.exists(filename)):            
            file = open(filename,'r') 
            locker.lock(file,locker.LOCK_EX) 
            jobid= int(file.read())   
            jobid += 1         
        file = open(filename,'w')    
        file.write(str(jobid))
        locker.unlock(file)            
        return jobid   
    

class FileLocker():
    'Python cookbook receipe 2.28 "File Locking Using a Cross-Platform API" '
    # needs win32all to work on Windows (NT, 2K, XP, _not_ /95 or /98)
    if os.name == 'nt':
        import win32con, win32file, pywintypes
        LOCK_EX = win32con.LOCKFILE_EXCLUSIVE_LOCK
        LOCK_SH = 0 # the default
        LOCK_NB = win32con.LOCKFILE_FAIL_IMMEDIATELY
        _overlapped = pywintypes.OVERLAPPED( )
        def lock(self,file, flags):
            hfile = win32file._get_osfhandle(file.fileno( ))
            win32file.LockFileEx(hfile, flags, 0, 0xffff0000,self._overlapped)
        def unlock(self,file):
            hfile = win32file._get_osfhandle(file.fileno( ))
            win32file.UnlockFileEx(hfile, 0, 0xffff0000,self._overlapped)
    elif os.name == 'posix':
        from fcntl import LOCK_EX, LOCK_SH, LOCK_NB
        def lock(self,file, flags):
            fcntl.flock(file.fileno( ), flags)
        def unlock(self,file):
            fcntl.flock(file.fileno( ), fcntl.LOCK_UN)
    else:
        raise RuntimeError("PortaLocker only defined for nt and posix platforms")
    
class IniFile(): 
    
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
            
    def write_ini_value_product(self,config=None, use_subdir=True,index_key=None):
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
                self.output_filename= ''.join((orig_output_filename,".",str(idx)))    
                dictionary = dict(zip(keys, element))
                # if no sub dir is generated, the index key can be used to generate a unique path later on
            if index_key is not None:
                dictionary[index_key]=idx
            self.write_ini(dictionary)
            output_filenames.append(self.output_filename)  
        return output_filenames

class Logger():
    
    def __init__(self,name='logger',level=logging.DEBUG,file=None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)                
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        if (file == None):
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)                
        else:
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)                  
            fh = logging.FileHandler(file)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
                
                
class Utilities():  
    
    def get_flatten_sequence(self,sequence):
        """get_flatten_sequence(sequence) -> list    
        Returns a single, flat list which contains all elements retrieved
        from the sequence and all recursively contained sub-sequences
        (iterables).
        Examples:
        >>> [1, 2, [3,4], (5,6)]
        [1, 2, [3, 4], (5, 6)]
        >>> get_flatten_sequence([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
        [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""    
        result = []
        for e in sequence:
            if hasattr(e, "__iter__") and not isinstance(e, basestring):
                result.extend(self.get_flatten_sequence(e))
            else:
                result.append(e)
        return result                
    
    def get_list_product(self,list_of_lists):
        # itertools.product() fails, when not all elements of the list are also lists.
        for idx, val in enumerate(list_of_lists):  
            if type(val) is not list:                
                list_of_lists[idx] = [val] 
        _list = []
        for element in itertools.product(*list_of_lists):
            _list.append(element)
        return _list              

    def substitute_template(self,template_filename,dictionary,output_filename=None):
        fh = open(template_filename,'r')
        content = fh.read()
        fh.close()
        mod_content = Template(content).safe_substitute(dictionary)
        if output_filename is None:
            output_filename = template_filename    
        fh = open(output_filename,'w')
        fh.write(mod_content)
        fh.close()
        

def get_cksum(self,filename, md5=True,exclude_line="", include_line=""):        
    """compute md5 for a file. allows to get md5 before including a line in the file or when excluding a specific line"""
    import hashlib
    cksum = None
    if md5:
        cksum = hashlib.md5()
    else:
        cksum = hashlib.sha224()
    for line in open(filename,"rb"):
        if exclude_line and line.startswith(exclude_line):
            continue
        cksum.update(line)
    cksum.update(include_line)
    return cksum.hexdigest()
     

        
              
class XmlValidator():    
    
    def __init__(self,xml_filename):
        self._filename = xml_filename

    def parsefile(self):
        parser = xml.parsers.expat.ParserCreate()
        parser.ParseFile(open(self._filename, "r"))

    def is_wellformatted(self): 
        try:
            self.parsefile()
            return True
        except Exception, e:
            sys.stderr.write(e)
            return False       
        
