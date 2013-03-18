#!/usr/bin/env python
'''
Created on Nov 29, 2011 by quandtan, behullar
Modified on Jan 11, 2012 by schmide
Modified on Feb 20, 2012 by schmide
Modified on Mar 6, 2012 by schmide, CHANGE_NAME enabled -> 0.1.2
Modified on Mar 26, 2012 by quandtan, key naming -> 0.1.3
Modified on Apr 3, 2012 by schmide, default: change name, stop on failure; key naming parameterized + defaults -> 0.1.4
Modified on May 10, 2012 by schmide, new applicake version -> 0.2.0
Modified on May 18, 2012 by schmide, new interface, contains set_args() -> 0.2.1
Modified on Sep 27, 2012 by schmide, allow both EXPERIMENT and DATASET_CODE as download keys for getexperiment -> 0.2.2
@author: quandtan, behullar, schmide
@version: 0.2.2
'''

import os,sys
from applicake.framework.interfaces import IWrapper

TRUES = ['TRUE', 'T', 'YES', 'Y', '1']
class NoDataSetFound(Exception):
    pass

class Dss(IWrapper):
    EXP_CODE = 'EXPERIMENT'
    DEFAULT_KEYS = {'getmsdata':'MZXML', 'getexperiment':'SEARCH'}
    ALLOWED_PREFIXES = ['getdataset', 'gettransitions', 'getmsdata', 'getexperiment']
    
    """
    Interface for application that wraps an external application
    """
    def prepare_run(self, info, log):
        """
        See interface
        """
        log.debug(info)
        prefix = info[self.PREFIX]
        info[self.DSSCLIENT] = prefix
        if not prefix in Dss.ALLOWED_PREFIXES:
            log.error("prefix ('%s') must be one of %s" % (prefix, Dss.ALLOWED_PREFIXES))
            sys.exit(1)
        self._result_filename = info['RESULT_FILE']
        if self._result_filename == '':
            self._result_filename = prefix+".out"
        if os.path.isfile(self._result_filename):
            os.remove(self._result_filename)
        
        dss_keys = info[self.DSSKEYS]
        if type(dss_keys) is str:
            self.outkeys = [key.strip() for key in dss_keys.split(',')]
        elif type(dss_keys) is list:
            self.outkeys = dss_keys
        else:
            log.error("%s (%s) must be either str or list" % (self.DSSKEYS, self.info[self.DSSKEYS]))
            sys.exit(2)
        while True:
            try: self.outkeys.remove('')
            except: break
        if len(self.outkeys) == 0:
            self.outkeys = [self.DSSOUTPUT]
            try: self.outkeys.append(Dss.DEFAULT_KEYS[prefix])
            except: pass
        
        if info[self.PREFIX] == 'getexperiment' and info.has_key(self.EXP_CODE):
            dscode_key = self.EXP_CODE
        else:
            dscode_key = self.DATASET_CODE
        if not info.has_key(dscode_key):
            log.error("%s (or %s) must be set in ini file" % (self.DATATSET_CODE, self.EXP_CODE))
            sys.exit(3)
        
        self._codes = set()
        dataset_codes = info[dscode_key]
        if type(dataset_codes) is str:
            self._codes.update([code.strip() for code in dataset_codes.split(',')])
        elif type(dataset_codes) is list:
            self._codes.update(dataset_codes)
        else:
            log.error("%s (%s) must be either str or list" % (dscode_key, self.info[dscode_key]))
            sys.exit(4)
        
        outdir = info[self.DATASET_DIR]
        if not os.path.isdir(outdir):
            if os.system("test -d %s" % outdir):
                log.error("value [%s] of key [%s] is not a directory" % (outdir,self.DATASET_DIR))
                sys.exit(5)
        
        if info['QUIET'].upper() in TRUES:
            voption = ''
        else:
            voption = '-v '
        
        if prefix == 'getmsdata' and not info['KEEP_NAME'].upper() in TRUES:
            koption = '-c '
        else:
            koption = ''
        
        self._failure_tolerant = info['FAILURE_TOLERANT'].upper() in TRUES
        
        print prefix
        print outdir
        print self._codes
        command = "%s --out=%s --result=%s %s%s%s" % (
                prefix, outdir, self._result_filename, 
                voption, koption,  " ".join(self._codes))
        return command, info
    
    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler.add_app_args(log, self.DATASET_DIR, 'download directory')
        args_handler.add_app_args(log, self.DATASET_CODE, 'data set code')
        args_handler.add_app_args(log, self.EXP_CODE, 'experiment code, can be used for getexperiment in lieu of %s (and to distinguish from the latter)' % self.DATASET_CODE)
        args_handler.add_app_args(log, self.DSSKEYS, "controls the output. results are values of these keys. "+
                                                     "the default is 'DSSOUTPUT' plus potentially a prefix depending key", default='')
        args_handler.add_app_args(log, self.PREFIX, "one of these executables: %s" % self.ALLOWED_PREFIXES, choices=self.ALLOWED_PREFIXES)
        args_handler.add_app_args(log, 'RESULT_FILE', "result file of the dss-client call, contains pathes to downloaded files. "+
                                                      "the default is the <prefix>.out", default='')
        args_handler.add_app_args(log, 'QUIET', "no messages written to stdout if set to true", default='False')
        args_handler.add_app_args(log, 'KEEP_NAME', "for prefix is 'gegmsdata' only: output keeps original file name if set to true "+
                                                       "(otherwise it will be changed to samplecode~dscode.mzXXML)", default='False')
        args_handler.add_app_args(log, 'FAILURE_TOLERANT', "exits with 0 in cases where no data set was found if to true", default='False')
        return args_handler
    
    def validate_run(self, info, log, run_code, out_stream, err_stream):
        """
        See interface
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
                        log.debug("add file '%s' for dataset %s to output" % (fl, ds))
                    except ValueError:
                        if not self._failure_tolerant:
                            raise NoDataSetFound(downloaded)
                        else:
                            log.error("No data set found for %s" % downloaded)
            # for single code requests: either add single file or array
            if len(self._codes) == 1:
                fstdsfls = dsfls.get(self._codes.pop())
                if None != fstdsfls and len(fstdsfls) == 1:
                    dssoutput = fstdsfls[0]
                else:
                    dssoutput = fstdsfls
            # for multi code requests: add the whole dictionary
            else:
                dssoutput = dsfls
            for outkey in self.outkeys:
                log.debug("add '%s' %s to ini" % (outkey, dssoutput))                                
                info[outkey.upper()] = dssoutput
            for keys in [ 'KEEP_NAME','FAILURE_TOLERANT','QUIET','RESULT_FILE']:
                if keys in info:
                    del info[keys]
        except Exception, e:
            log.critical("Validation of result file failed: %s %s" % (e.__class__.__name__, e))
            exit_code = 1
        return exit_code, info
