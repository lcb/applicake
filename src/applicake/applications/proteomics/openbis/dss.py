#!/usr/bin/env python
'''
Created on Nov 29, 2011 by quandtan, behullar
Modified on Jan 11, 2012 by schmide
Modified on Feb 20, 2012 by schmide
Modified on Mar 6, 2012 by schmide, CHANGE_NAME enabled -> 0.1.2
Modified on Mar 26, 2012 by quandtan, key naming -> 0.1.3
Modified on Apr 3, 2012 by schmide, default: change name, stop on failure; key naming parameterized + defaults -> 0.1.4
Modified on May 10, 2012 by schmide, new applicake version -> 0.2.0
@author: quandtan, behullar, schmide
@version: 0.2.0
'''

import os,sys,shutil
from applicake.framework.interfaces import IWrapper
from applicake.framework.enums import KeyEnum

TRUES = ['TRUE', 'T', 'YES', 'Y', '1']
class NoDataSetFound(Exception):
    pass

class Dss(IWrapper):
    DEFAULT_KEYS = {'getmsdata':'MZXML', 'getexperiment':'SEARCH'}
    MANDATORY_KEYS = ['DATASET_CODE', 'DATASET_DIR']
    ALLOWED_PREFIXES = ['getdataset', 'gettransitions', 'getmsdata', 'getexperiment']
    
    '''
    this is a workaround for the seemingly disfunctional log
    '''
    def _log(self, cmet, level, msg):
        cmet(msg)
        print "%s: %s" % (level,msg)

    """
    Interface for application that wraps an external application
    """
    def prepare_run(self, info, log):
        """
        Prepare the execution of an external program.
        
        @type info: dict         
        @param info: Dictionary object with information needed by the class
        @type log: Logger 
        @param log: Logger to store log messages 
        
        @rtype: (string,dict)
        @return: Tuple of 2 objects; the command to execute and the (updated) info object.
        """
        self._log(log.info, 'INFO', info)
        prefix = info[KeyEnum.prefix_key]
        info['DSSCLIENT'] = prefix
        if not prefix in Dss.ALLOWED_PREFIXES:
            self._log(log.error, 'ERROR', "prefix ('%s') must be one of %s" % (prefix, Dss.ALLOWED_PREFIXES))
            sys.exit(1)
        self._result_filename = prefix+".out"
        try: os.remove(self._result_filename)
        except: pass
        for key in Dss.MANDATORY_KEYS:
            try: info[key]
            except KeyError:
                self._log(log.error, 'ERROR', "Missing mandatory property in inifile: %s" % key)
                sys.exit(2)
        # output is written to all ini-properties who's keys are listed in in Dss.outkeys.
        # if the keys are not given as ini property 'DSSKEYS', 
        # the default is 'DSSOUTPUT' plus an optional, prefix specific key.
        try: 
            dss_keys = info['DSSKEYS']
            if type(dss_keys) is str: self.outkeys = [dss_keys]
            elif type(dss_keys) is list: self.outkeys = dss_keys
            else: raise Exception('goto except')
        except:
            self.outkeys = ['DSSOUTPUT']
            try: self.outkeys.append(Dss.DEFAULT_KEYS[prefix])
            except: pass
        dataset_codes = info['DATASET_CODE']
        if type(dataset_codes) is str:
            self._codes = [code.strip() for code in dataset_codes.split(',')]
        elif type(dataset_codes) is list:
            self._codes = dataset_codes
        else:
            self._log(log.error, 'ERROR', "DATASET_CODE must be either str or list")
            sys.exit(3)
        outdir = info['DATASET_DIR']
        if not os.path.isdir(outdir):
            if os.system("test -d %s" % outdir):
                self._log(log.error, 'ERROR', "%s (DATASET_DIR) is not a directory" % outdir)
                sys.exit(4)
        if info.get('QUIET', '').upper() in TRUES:
            voption = ''
        else:
            voption = '-v '
        if prefix == 'getmsdata' and not info.get('KEEP_NAME', '').upper() in TRUES:
            print 'change name on'
            koption = '-c '
        else:
            koption = ''
        self._failure_tolerant = info.get('FAILURE_TOLERANT', '').upper() in TRUES
        print prefix
        print outdir
        print self._codes
        command = "%s --out=%s --result=%s %s%s%s" % (
                prefix, outdir, self._result_filename, 
                voption, koption,  " ".join(self._codes))
        return command, info
        raise NotImplementedError("prepare_run() is not implemented")  
       
    def validate_run(self, info, log, run_code, out_stream, err_stream):
        """
        Validate the execution of the external application. 
        (e.g. output parsing)
        
        @type info: dict         
        @param info: Dictionary object with information needed by the class
        @type log: Logger 
        @param log: Logger to store log messages 
        @type run_code: int
        @param run_code: Exit code of the process prepared with prepare_run() 
        @type out_stream: Stream
        @param out_stream: Stream object with the stdout of the executed process
        @type err_stream: Stream 
        @param err_stream: Stream object with the stderr of the executed process 
        
        @rtype: (int,dict)
        @return: Tuple of 2 objects; the exit code and the (updated) info object. 
        """
        exit_code = 0
        for (stream, logf, logt) in [[out_stream, log.debug, 'OUTPUT'], [err_stream, log.error, 'ERROR']]:
            try:
                strd = stream.read()
                if len(strd)>0:
                    logf("%s from dss-client:\n%s" % (logt, strd))
            except:
                pass
        try:
            dsfls = dict()
            with open(self._result_filename,'r') as resfil:
                for downloaded in [ line.strip() for line in resfil.readlines() ]:
                    try:
                        ds, fl = downloaded.split("\t")
                        dsfls.setdefault(ds, []).append(fl)
                        self._log(log.debug, 'DEBUG', "add file '%s' for dataset %s to output" % (fl, ds))
                    except ValueError:
                        if not self._failure_tolerant:
                            raise NoDataSetFound(downloaded)
                        else:
                            self._log(log.error, 'ERROR', "No data set found for %s" % downloaded)
            # for single code requests: either add single file or array
            if len(self._codes) == 1:
                fstdsfls = dsfls.get(self._codes[0])
                if None != fstdsfls and len(fstdsfls) == 1:
                    dssoutput = fstdsfls[0]
                else:
                    dssoutput = fstdsfls
            # for multi code requests: add the whole dictionary
            else:
                dssoutput = dsfls
            for outkey in self.outkeys:
                self._log(log.debug, 'DEBUG', "add '%s' %s to ini" % (outkey, dssoutput))                                
                info[outkey.upper()] = dssoutput
        except Exception, e:
            self._log(log.error, 'ERROR', "Validation of result file failed: %s %s" % (e.__class__.__name__, e))
            exit_code = 1
        return exit_code, info

if "__main__" == __name__:
    # init the application object (__init__)
    a = Dss(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)        
