'''
Created on Mar 31, 2012

@author: quandtan
'''

import fcntl
import errno
import gzip
import os
import shutil
import StringIO
import sys
import urllib2

class FileLocker(object):
    """
    File locking that works across platforms.
    """
    # Python cookbook receipe 2.28 "File Locking Using a Cross-Platform API"
    # needs win32all to work on Windows (NT, 2K, XP, _not_ /95 or /98)
    if os.name == 'nt':
        import win32con, win32file, pywintypes
        LOCK_EX = win32con.LOCKFILE_EXCLUSIVE_LOCK
        LOCK_SH = 0 # the default
        LOCK_NB = win32con.LOCKFILE_FAIL_IMMEDIATELY
        _overlapped = pywintypes.OVERLAPPED( )
        def lock(self,fh, flags):
            hfile = win32file._get_osfhandle(fh.fileno( ))
            win32file.LockFileEx(hfile, flags, 0, 0xffff0000,self._overlapped)
        def unlock(self,fh):
            hfile = win32file._get_osfhandle(fh.fileno( ))
            win32file.UnlockFileEx(hfile, 0, 0xffff0000,self._overlapped)
    elif os.name == 'posix':        
        from fcntl import LOCK_EX, LOCK_SH, LOCK_NB
        def lock(self,fh, flags):
            fcntl.flock(fh.fileno(), flags)
        def unlock(self,fh):
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
    else:
        raise RuntimeError("PortaLocker only defined for nt and posix platforms")
    

class FileUtils(object):
    """
    Utilites for handling files and directories
    """
    
    @staticmethod
    def download_url(log,url,path):
        """
        Download a file from an internet url and stores it in a local path.
        """
        u = urllib2.urlopen(url)
        localFile = open(path, 'wb')
        localFile.write(u.read())
        localFile.close()
        log.debug('downloaded [%s] and saved it as [%s]' % (url,path))
        
    
    @staticmethod
    def is_valid_file(log,path):
        """
        Check if a file is valid.
        
        Checks if file exists, if it is a file, if it can be read and 
        if file size i larger 0 KB.
        
        @type log: Logger
        @param log: Logger to store log messages 
        @type path: string
        @param path: Path of a file
        
        @rtype: Boolean
        @return: True if the file is valid, otherwise False 
        """
        
        if not os.path.exists(path):
            log.error('path [%s] does not exist' % path)
            return False                
        if not os.path.isfile(path):
            log.error('path [%s] is no file' % path)
            return False
        if not os.access(path,os.R_OK):
            log.error('file [%s] cannot be read' % path)
            return False
        if not (os.path.getsize(path) > 0):
            log.error('file [%s] is 0KB' % path)
            return False
        else:
            log.debug('file [%s] checked successfully' % path)  
            return True  
    
    @staticmethod
    def get_cksum(self,path, md5=True,exclude_line="", include_line=""):        
        """
        Compute md5 for a file. allows to get md5 before including a line in the file
         or when excluding a specific line
         
         Arguments:
         - path: path of the file
         - md5: if true uses md5, otherwise sha224 is used
           (default: md5)
         - exclude_line: line to exclude from calucation
         - include_line: line to include into calculation
         
         Return checksum
        """
        import hashlib
        cksum = None
        if md5:
            cksum = hashlib.md5()
        else:
            cksum = hashlib.sha224()
        for line in open(path,"rb"):
            if exclude_line and line.startswith(exclude_line):
                continue
            cksum.update(line)
        cksum.update(include_line)
        return cksum.hexdigest()    
    
    @staticmethod
    def makedirs_safe(log,path,clean=False):
        """
        Recursively create directories in 'path' unless they already exist.
        Safe to use in a concurrent fashion.
        
        Arguments:
        -log: Logger
        - path: the directory path
        - clean: if True, the content of the directory is deleted if it exists
          (default: False)    
        """
        try:
            os.makedirs(path)
            os.chmod(path, 0777)
            log.debug('dir [%s] was created' % path)
        except OSError as error:
            if error.errno == errno.EEXIST and os.path.isdir(path):
                log.debug('dir [%s] already exists' % path)
                #TODO: should remove the existing directory and create it newly
                # content of the old directory should be put into the log  
                if clean:
                    FileUtils.rm_dir_content(path)
                    FileUtils.makedirs_safe(log,path,clean=False)
            else:
                log.fatal('could not create dir [%s]' % path)
                sys.exit(1)
    
    @staticmethod
    def decompress(input,output,type):
        if type == 'gz':
            fin = gzip.open(input, 'rb')
            fout = open(output,'w+')
            fout.write(fin.read())
            fin.close()
               
    
    @staticmethod
    def rm_dir_content(path):
        """
        Delete the content of a directory without deleting the directory itself
        
        Arguments:
        - path: path of the directory
        
        Return: Tuple of 2 values. The first is a boolean and the second a string
        containing a message that explains the boolean (+ the content that was removed)
        """
        success = True
        msg = ['File content:']    
        for root, dirs, files in os.walk(path):            
            for f in files:
                try:
                    os.unlink(os.path.join(root, f))
                    msg.append(f)
                except:
                    success = False
                    msg.append('COULD NOT UNLINK FILE [%s]' % f)
                    return (success,';'.join(msg))
                msg.append(f)
            for d in dirs:
                try:
                    shutil.rmtree(os.path.join(root, d))
                    msg.append(d)
                except:
                    success = False
                    msg.append('COULT NOT REMOVE DIR [%s]' % d)
                    return (success,';'.join(msg))
        return (success,';'.join(msg))
        
        