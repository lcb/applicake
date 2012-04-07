'''
Created on Mar 31, 2012

@author: quandtan
'''

import errno
import os
import shutil

class FileUtils(object):
    """
    Utilites for handling files and directories
    """
    @staticmethod
    def is_valid_file(self,path):
        """
        Check if a file is valid
        
        Checks if file exists, if it is a file, if it can be read and 
        if file size i larger 0 KB 
        
        Arguments:
        - path:  path of a file
        
        Return: Tuple of 2 values. The first is a boolean and the second a string
        containing a message that explains the boolean
        """
        valid = False
        msg = ''
        fail1 = not os.path.exists(path)
        fail2 = not os.path.isfile(path)
        fail3 = not os.access(path,os.R_OK)
        fail4 = not (os.path.getsize(path) > 0)
        fails = [fail1,fail2,fail3,fail4]
        if any(fails):
            msg = '''file [%s] does not exist [%s], 
            is not a file [%s], cannot be read [%s] or
            has no file larger that > 0kb [%s]''' % (
                                                            os.path.abspath(path),
                                                            fail1,fail2,fail3,fail4
                                                            )
        else:
            msg = 'file [%s] checked successfully' % path  
            valid = True
        return (valid,msg)  
    
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
    def makedirs_safe(path,clean=False):
        """
        Recursively create directories in 'path' unless they already exist.
        Safe to use in a concurrent fashion.
        
        Arguments:
        - path: the directory path
        - clean: if True, the content of the directory is deleted if it exists
          (default: False) 
        
        Return: Tuple of 2 values. The first is a boolean and the second a string
        containing a message that explains the boolean        
        """
        success = None
        msg = ''
        try:
            os.makedirs(path)
            msg = 'dir [%s] was created' % path
            success = True
        except OSError as error:
            if error.errno == errno.EEXIST and os.path.isdir(path):
                msg = 'dir [%s] already exists' % path
                #TODO: should remove the existing directory and create it newly
                # content of the old directory should be put into the log  
                if clean:
                    
                    FileUtils.rm_dir_content(path)
                success = True
                pass
            else:
                msg = 'could not create dir [%s]' % path
                success = False
        return(success,msg)
    
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
        