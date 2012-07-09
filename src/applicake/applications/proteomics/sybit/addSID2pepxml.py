'''
Created on Jul 5, 2012

@author: lorenz
'''
import os
import re
from applicake.framework.interfaces import IApplication


class AddSID2pepxml(IApplication):
    
    def main(self,info,log):
        
        outfiles = []
        for infile in info['PEPXMLS']:
            path,ext = os.path.splitext(infile)
            filename,ext = os.path.splitext(os.path.basename(infile))
            outfile = os.path.join(info[self.WORKDIR], filename + '_corrected' + ext)
            
            
            fin = open(infile)
            fout = open(outfile,'wb')
            not_found = True
            for line in fin:
                if not_found:
                    if '<search_summary' in line:
                        line = '%s search_id="1">\n' % re.sub('>$', '', line)
                        not_found = False
                fout.write(line)
            
            fin.close()
            fout.close()
            outfiles.append(outfile)
            
            if not_found:
                log.critical('file [%s] did not contain the line pattern [<search_summary]' % infile)
                return 1,info
          
        info['PEPXMLS'] = outfiles
        return 0,info
    
    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, 'PEPXMLS' , 'Base name for collecting output files (e.g. from a parameter sweep)')
        args_handler.add_app_args(log, self.WORKDIR, 'Workdir)')
        
        return args_handler
