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
    Download a dat file from a specific url and stores it as local file.
    """

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._result_file = '%s.dat' % base # result produced by the application

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
        info[self.DAT] = self._result_file
        FileUtils.download_url(log, info[self.URL_DAT], info[self.DAT])
        return 0,info