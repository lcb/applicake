#!/usr/bin/env python
'''
Performs rsync copy with the 'COPY' key in the input-ini and creates COPYOUTPUT 
key with a list of copied files (absolute paths) when sucessful. Needs passwordless SSH for network copies 
(prevents hangup). Does parameter optimization for local copies. 

Required args: -i input.ini (with COPY key) -o output.ini (with COPYOUT file list)

Created on Feb 20, 2012

@author: lorenz
'''

import sys

from applicake.framework.interfaces import IWrapper

class Copier(IWrapper):
    def prepare_run(self, info, log):
        
        #get path to copy
        path = info['COPY']

        #if it is a local copy add special local options
        localparams = ''
        if path.find(":") == -1:
            localparams = "-l" #l=copy links as links
            
        #assemble rsync command. u=update (not because out sonst wrong) r=recursive (folders) 
        #t=preserve time z=compress network traffic 
        command = "rsync -e 'ssh -o PreferredAuthentications=publickey,hostbased' -vrtz " + localparams + " " + path
        return command,info
           
    def validate_run(self,info,log, run_code,out_stream, err_stream): 

        #if everything fine write output.ini
        if run_code == 0:
            out_stream.readline() #skip header "building file list"
            copyoutput = []
            outdir = info["COPY"].split()[1]+'/'
            for line in out_stream.readlines():
                line = line.strip()
                if line == '': #skip tail
                    break
                else:
                    copyoutput.append(outdir+line)
            log.debug("Adding key COPYOUTPUT to ini: " + str(copyoutput)) 
            info['COPYOUTPUT'] = copyoutput
        else:
            if run_code == 12:
                log.fatal("No access to destination (check permissions & existence)")    
            elif run_code == 23:
                log.fatal("No access to source (or destination) (check permissions & existence)")
            elif run_code == 255:
                log.fatal("Connection problem (check passwordless ssh & if server is up)")
            else:
                log.fatal("A unexpected copy error ocurred")
        
        #return run_code to next layer        
        return (run_code,info)
