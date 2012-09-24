#!/usr/bin/env python
'''
Based on pepxmlcorrector, may be merged into later.

Created on Feb 20, 2012

@author: lorenz
'''

import os, sys

from applicake.framework.interfaces import IApplication

class SequestPepxmlCorrector(IApplication):
    
    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, 'NEWBASENAME' , 'New styple base name')
        args_handler.add_app_args(log, self.DESTINATION, 'Former rsync destination')
        args_handler.add_app_args(log, self.WORKDIR, 'Workdir')
        
        return args_handler
       
    def main(self,info,log):
        #get required args. NEWBASENAME is to replace mzXML filenames in search results with new
        newbasename = info['NEWBASENAME']
        
        #the workdir aus automatical created by WFApp and used to mk cleanpepxml path
        copiedpepxml = info[self.DESTINATION][0]
        cleanpepxmldir = info[self.WORKDIR]
        cleanpepxmlname = os.path.basename(copiedpepxml)
        cleanpepxml = os.path.join(cleanpepxmldir, cleanpepxmlname)
        info['PEPXMLS'] = [cleanpepxml]  
        
        log.debug("CREATING CLEANPEPXML " + cleanpepxml)
        r = open(copiedpepxml)
        oldbasename = ''
        for line in r.readlines():
            if 'base_name' in line:
                oldbasename = line.split('base_name="')[1].split('" ')[0]
                break
        r.close()
        
        if oldbasename == '':
            log.fatal("No base_name found in " + copiedpepxml);
            sys.exit(1)
        else:
            log.debug("Oldbasename " + oldbasename+" being replaced with " + newbasename)
            
        r = open(copiedpepxml)
        w = open(cleanpepxml, "w")
        for line in r.readlines():
            line = line.replace('="'+oldbasename, '="'+newbasename)   
            w.write(line + "\n")
        r.close()
        w.close()

        return 0,info
