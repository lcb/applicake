'''
Created on Dec 14, 2010

@author: quandtan
'''

import logging,itertools,os,fcntl,time,random
#import win32con, win32file, pywintypes,fcntl
from configobj import ConfigObj #easy_install configobj
from string import Template

class Generator():
    
    def job_id(self,dirname):
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
    
    def __init__(self,in_filename,out_filename=None,lock=False):
        self._in_filename = in_filename 
        if out_filename is None:       
            self._out_filename = in_filename
        else:
            self._out_filename = out_filename
        self._lock = lock
        
    def add_to_ini(self,dictionary):
#        locker = FileLocker()        
#        file = open(self._in_filename,'r')
#        locker.lock(file,locker.LOCK_EX)
        config = self.read_ini()
        config.update(dictionary)
        self.write_ini(config)        
#        locker.unlock(file)         
        
    def read_ini(self): 
        'Read file in windows ini format and returns a dictionary like object (ConfigObj)'
        if not self._lock:
            return ConfigObj(self._in_filename)
        else:
            locker = FileLocker()
            file = open(self._in_filename,'r')        
            locker.lock(file,locker.LOCK_EX)
            config = ConfigObj(self._in_filename)
            locker.unlock(file)       
            return config        
    
    def write_ini(self,dictionary):
        config = ConfigObj(dictionary)
        config.filename = self._out_filename
        if not self._lock:
            config.write()
        else:        
            locker = FileLocker()
            file = open(self._out_filename,'r')
            locker.lock(file,locker.LOCK_EX)
            config.write()
            locker.unlock(file)
            
    def write_ini_value_product(self,config=None, use_subdir=True,index_key=None):
        'Takes an ini file as input and generates a new ini file for each value combination'
        out_filenames = []
        if config is None:
            config = self.read_ini()
        keys = config.keys()
        values = config.values()
        elements = Utilities().get_list_product(values)
        orig_out_filename = self._out_filename
        for idx,element in enumerate(elements): 
            dictionary = None
            if use_subdir:
                dir = os.path.dirname(orig_out_filename)               
                sub_dir = os.path.join(dir,str(idx))
                os.mkdir(sub_dir)
                self._out_filename=os.path.join(sub_dir,os.path.basename(orig_out_filename))
                dictionary = dict(zip(keys, element))
                dictionary['DIR'] = sub_dir
            else:                           
                self._out_filename= ''.join((orig_out_filename,".",str(idx)))    
                dictionary = dict(zip(keys, element))
                # if no sub dir is generated, the index key can be used to generate a unique path later on
            if index_key is not None:
                dictionary[index_key]=idx
            self.write_ini(dictionary)
            out_filenames.append(self._out_filename)  
        return out_filenames

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
    
    def get_list_product(self,list_of_lists):
        # itertools.product() fails, when not all elements of the list are also lists.
        for idx, val in enumerate(list_of_lists):  
            if type(val) is not list:                
                list_of_lists[idx] = [val] 
        _list = []
        for element in itertools.product(*list_of_lists):
            _list.append(element)
        return _list              

    def substitute_template(self,template_filename,dictionary,out_filename=None):
        fh = open(template_filename,'r')
        content = fh.read()
        fh.close()
        mod_content = Template(content).safe_substitute(dictionary)
        if out_filename is None:
            out_filename = template_filename    
        fh = open(out_filename,'w')
        fh.write(mod_content)
        fh.close()
        
#    def mk_subdir(self,base_dirname):
#        sub_dirname = random.
#        basedir = os.path.join(base_dirname,) 
        

        
    
        
                       
#print list(itertools.product(['a1','a2','a3'], ['b1','b2','b3'],['c1','c2','c3','c4','c5'],['d1','d2']))
#somelists = [['a1','a2','a3'], ['b1','b2','b3'],['c1','c2','c3','c4','c5'],['d1','d2']]
#for element in itertools.product(*somelists):
#    print element
