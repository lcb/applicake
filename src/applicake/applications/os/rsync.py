#!/usr/bin/env python
'''
Created on Feb 20, 2012

@author: lorenz, quandtan
'''

from applicake.framework.interfaces import IWrapper

class Rsync(IWrapper):
    """
    Performs rsync copy with the 'COPY' key in the input-ini and creates COPYOUTPUT 
    key with a list of copied files (absolute paths) when sucessful. Needs passwordless SSH for network copies 
    (prevents hangup). Does parameter optimization for local copies.   
    """
    def prepare_run(self, info, log):
        """
        See super class.
        
        @precondition: 'info' object has to contain the following key [%s,%s]
        """% (self.src_key,self.dest_key)
        
        #get path to copy
        path = info[self.src_key]
        #if it is a local copy add special local options
        localparams = ''
        if path.find(":") == -1:
            localparams = "-l" #l=copy links as links            
        #assemble rsync command. u=update (not because out sonst wrong) r=recursive (folders) 
        #t=preserve time z=compress network traffic 
        command = "rsync -e 'ssh -o PreferredAuthentications=publickey,hostbased' -vrtz " + localparams + " " + path
        return command,info
           
    def validate_run(self,info,log, run_code,out_stream, err_stream): 
        """
        See super class.
        """

        #if everything fine write output.ini
        if run_code == 0:
            out_stream.readline() #skip header "building file list"
            copyoutput = []
            outdir = info[self.src_key].split()[1]+'/'
            for line in out_stream.readlines():
                line = line.strip()
                if line == '': #skip tail
                    break
                else:
                    copyoutput.append(outdir+line)
            log.debug("Adding key COPYOUTPUT to ini: " + str(copyoutput)) 
            info[self.dest_key] = copyoutput
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
