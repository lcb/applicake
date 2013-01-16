'''
Created on Aug 14, 2012

@author: blum, wolski
'''

from applicake.framework.interfaces import IApplication

class KeyExtract(IApplication):

    def main(self,info,log):
        """
        See interface.
        """
        for line in open(info['KEYFILE']):
            for key in info['KEYSTOEXTRACT']:
                if line.startswith(key):
                    value = line.split()[2]
                    log.debug('ADDING key %s value %s to inifile' % (key,value))
                    info[key] = value
        return 0,info

    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, 'KEYFILE', 'File to extract keys from') 
        args_handler.add_app_args(log, 'KEYSTOEXTRACT', 'which keys to extract',action='append') 
        return args_handler
