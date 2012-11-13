'''
Created on Nov 13, 2012

@author: quandtan
'''

import os
from applicake.framework.interfaces import IApplication
from applicake.utils.fileutils import FileUtils

class Downloader(IApplication):
    '''
    Application that downloads a file from an url to process further.
    '''
    _result_file = ''

    def set_args(self,log,args_handler):
        """
        See super class.
        """
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory')
        return args_handler
    
    def download_(self,info,log):
        url = info[self.URL_DAT]
        path = self._result_file
        FileUtils.download_url(log, url, path)

class DatDownloader(Downloader): 
    """
    Download a dat.gz file from a specific url, decompress it and stores it as local file.
    """

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._result_file = '%s.dat' % base # result produced by the application
        self._result_file2 = '%s.dat.gz' % base # result produced by the application

    def set_args(self,log,args_handler):
        """
        See super class.
        """
        args_handler = super(DatDownloader, self).set_args(log,args_handler)
        args_handler.add_app_args(log, self.URL_DAT, 'Url to download the .dat file')
        return args_handler 
         
 
    def main(self,info,log):
        '''      
        '''
        key = self.DAT
        wd = info[self.WORKDIR]
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        self._result_file = os.path.join(wd,self._result_file)
        info[key] = self._result_file
        self._result_file2 = os.path.join(wd,self._result_file2)
        log.debug('download [%s] to [%s]' % (info[self.URL_DAT],self._result_file2))
        FileUtils.download_url(log, info[self.URL_DAT], self._result_file2)
        log.debug('decompress [%s] to [%s]' % (self._result_file,self._result_file2))
        FileUtils.decompress(self._result_file2, info[key], type='gz')
        return 0,info