'''
Created on Jan 20, 2013

@author: lorenz
'''

from applicake.framework.interfaces import IApplication

class FDR2iProphetProbability(IApplication):
    def main(self,info,log):
        """
        See interface.
        """
        minprob = ''
        for line in open(info['PEPXMLS']):
            if line.startswith('<error_point error="%s' % info['FDR']):
                minprob = line.split(" ")[2].split("=")[1].replace('"','')
                break
            
        if minprob != '':
            log.info(minprob)
            info['IPROBABILITY'] = minprob    
            return 0,info
        else:
            log.error("error point for fdr not found")
            return 1,info

    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, 'PEPXMLS', 'pepxml to extract value from') 
        args_handler.add_app_args(log, 'FDR', 'which keys to extract',action='append') 
        return args_handler
