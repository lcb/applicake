#!/usr/bin/env python
'''
Created on Nov 29, 2011 by quandtan, behullar
Modified on Jan 11, 2012 by schmide
Modified on Feb 20, 2012 by schmide
Modified on Mar 6, 2012 by schmide, CHANGE_NAME enabled -> 0.1.2
Modified on Mar 26, 2012 by quandtan, key naming -> 0.1.3
Modified on Apr 3, 2012 by schmide, default: change name, stop on failure; key naming parameterized + defaults -> 0.1.4
@author: quandtan, behullar, schmide
@version: 0.1.4
'''

import os,sys,shutil
from applicake.app import WorkflowApplication
from applicake.utils import XmlValidator

TRUES = ['TRUE', 'T', 'YES', 'Y', '1']
class NoDataSetFound(Exception):
    pass

class Dss(WorkflowApplication):
    STDOUT_DMP = '.std.out'
    STDERR_DMP = '.std.err'
    DEFAULT_KEYS = {'getmsdata':'MZXML', 'getexperiment':'SEARCH'}
    MANDATORY_KEYS = ['DATASET_CODE', 'DATASET_DIR']
    ALLOWED_PREFIXES = ['getdataset', 'gettransitions', 'getmsdata', 'getexperiment']
    
    def _get_command(self,prefix,input_filename):
        if not prefix in Dss.ALLOWED_PREFIXES:
            self.log.error("prefix ('%s') must be one of %s" % (prefix, Dss.ALLOWED_PREFIXES))
            sys.exit(1)
        self._result_filename = prefix+".out"
        config = self._iniFile.read_ini()
        for key in Dss.MANDATORY_KEYS:
            try: config[key]
            except KeyError:
                self.log.error("Missing mandatory property in inifile: %s" % key)
                sys.exit(2)
        # output is written to all ini-properties who's keys are listed in in Dss.outkeys.
        # if the keys are not given as ini property 'DSSKEYS', 
        # the default is 'DSSOUTPUT' plus an optional, prefix specific key.
        try: 
            dss_keys = config['DSSKEYS']
            if type(dss_keys) is str: self.outkeys = [dss_keys]
            elif type(dss_keys) is list: self.outkeys = dss_keys
            else: raise Exception('goto except')
        except:
            self.outkeys = ['DSSOUTPUT']
            try: self.outkeys.append(Dss.DEFAULT_KEYS[prefix])
            except: pass
        dataset_codes = config['DATASET_CODE']
        if type(dataset_codes) is str:
            self._codes = [code.strip() for code in dataset_codes.split(',')]
        elif type(dataset_codes) is list:
            self._codes = dataset_codes
        else:
            self.log.error("DATASET_CODE must be either str or list")
            sys.exit(3)
        outdir = config['DATASET_DIR']
        if not os.path.isdir(outdir):
            if os.system("test -d %s" % outdir):
                self.log.error("%s (DATASET_DIR) is not a directory" % outdir)
                sys.exit(4)
        if config.get('QUIET', '').upper() in TRUES:
            voption = ''
        else:
            voption = '-v '
        if prefix == 'getmsdata' and not config.get('KEEP_NAME', '').upper() in TRUES:
            print 'change name on'
            koption = '-c '
        else:
            koption = ''
        self._failure_tolerant = config.get('FAILURE_TOLERANT', '').upper() in TRUES
        self._iniFile.add_to_ini({'DSSCLIENT':prefix})
        print prefix
        print outdir
        print self._codes
        return "%s --out=%s --result=%s %s%s%s >%s 2>%s" % (
                prefix, outdir, self._result_filename, 
                voption, koption,  " ".join(self._codes),
                Dss.STDOUT_DMP, Dss.STDERR_DMP)
      
    def _validate_run(self,run_code):
        exit_code = 0
        for (dmp, info, type_) in [[Dss.STDOUT_DMP, self.log.debug, 'OUTPUT'], [Dss.STDERR_DMP, self.log.error, 'ERROR']]:
            try:
                if os.path.getsize(dmp) > 0:
                    dmpfile = open(dmp)
                    info("%s from dss-client:\n%s" % (type_, dmpfile.read()))
                    dmpfile.close()
            except:
                pass
        try:
            dsfls = dict()
            with open(self._result_filename,'r') as resfil:
                for downloaded in [ line.strip() for line in resfil.readlines() ]:
                    try:
                        ds, fl = downloaded.split("\t")
                        dsfls.setdefault(ds, []).append(fl)
                        self.log.debug("add file '%s' for dataset %s to output" % (fl, ds))
                    except ValueError:
                        if not self._failure_tolerant:
                            raise NoDataSetFound(downloaded)
                        else:
                            self.log.error("No data set found for %s" % downloaded)
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
                self.log.debug("add '%s' %s to ini" % (outkey, dssoutput))                                
                self._iniFile.add_to_ini({outkey.upper():dssoutput})
        except Exception, e:
            self.log.error("Validation of result file failed: %s %s" % (e.__class__.__name__, e))
            exit_code = 1
        self.stdout.seek(0) # to reset the pointer so that super method works properly
        return super(Dss, self)._validate_run(run_code) or exit_code
      
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
