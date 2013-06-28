"""
Created on Mar 31, 2012

@author: quandtan
"""

import errno
import os
import shutil
import sys


class FileUtils(object):
    """
    Utilites for handling files and directories
    """

    @staticmethod
    def is_valid_file(log, path):
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
        if not os.access(path, os.R_OK):
            log.error('file [%s] cannot be read' % path)
            return False
        if not (os.path.getsize(path) > 0):
            log.error('file [%s] is 0KB' % path)
            return False
        else:
            log.debug('file [%s] checked successfully' % path)
            return True

    @staticmethod
    def makedirs_safe(log, path, clean=False):
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
            os.chmod(path, 0775)
            #log.debug('dir [%s] was created' % path)
        except OSError as error:
            if error.errno == errno.EEXIST and os.path.isdir(path):
                log.debug('dir [%s] already exists' % path)
                #TODO: should remove the existing directory and create it newly
                # content of the old directory should be put into the log  
                if clean:
                    FileUtils.rm_dir_content(path)
                    FileUtils.makedirs_safe(log, path, clean=False)
            else:
                log.fatal('could not create dir [%s]' % path)
                sys.exit(1)


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
                    return success, ';'.join(msg)
                msg.append(f)
            for d in dirs:
                try:
                    shutil.rmtree(os.path.join(root, d))
                    msg.append(d)
                except:
                    success = False
                    msg.append('COULT NOT REMOVE DIR [%s]' % d)
                    return success, ';'.join(msg)
        return success, ';'.join(msg)
        
        
