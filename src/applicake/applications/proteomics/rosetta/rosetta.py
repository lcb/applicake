'''
Created on May 10, 2012

@author: loblum
'''

import os
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler

class Rosetta(IWrapper):
    """
    Wrapper for minirosetta.default.linuxgcc
    """
    
    def __init__(self):
        base = self.__class__.__name__
        self._default_prefix = 'minirosetta.default.linuxgccrelease'
        self._template_file = '%s.tpl' % base 
        self._result_file = 'default.out'     

    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info  
    
    def get_template_handler(self):
        """
        return Template handler
        """
        return RosettaTemplate()    
    
    def prepare_run(self,info,log):
        """
        See interface.      
        @precondition: info object need the key [%s]
        """ % self.TEMPLATE
        wd = info[self.WORKDIR]
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        self._template_file = os.path.join(wd,self._template_file) 
        info['TEMPLATE'] = self._template_file 
        self._result_file = os.path.join(wd,self._result_file) 
        info['ROSETTAOUT'] = self._result_file  
        
        log.debug('get template handler')
        th = self.get_template_handler()
        log.debug('modify template')                
        mod_template,info = th.modify_template(info, log)        
        prefix,info = self.get_prefix(info,log)
        #FIXME: template db are given  by cmdline to have correct expansion to n files 
        command = "%s @%s -in:file:template_pdb %s/*.pdb" %(prefix,info['TEMPLATE'],info['ROSETTAINPUTDIR']) 
        return command,info  
    
    def set_args(self,log,args_handler):
        """
        See interface
        """    
        args_handler.add_app_args(log, 'ROSETTAINPUTDIR', 'Peak list file in mgf format')     
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')  
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory') 
        return args_handler      
    
    def validate_run(self,info,log,run_code, out_stream, err_stream):
        """
        See interface
        """
        if 0 != run_code:
            return run_code,info
        return 0,info  

class RosettaTemplate(BasicTemplateHandler):
    """
    Template handler for Xtandem.  
    """
    def read_template(self, info, log):
        """
        loblum: changed here
        """
        template = """
# module load rosetta (no need to specify the Rosetta database)
-run:protocol threading
-run:shuffle

# alignment.filt is an input file
-in:file:alignment $ROSETTAINPUTDIR/alignment.filt
-cm:aln_format grishin

# files that start with aat000 are fragment files, 03 and 09 refers to length of fragments (always same name)
-frag3 $ROSETTAINPUTDIR/aat000_03_05.200_v1_3.gz
-frag9 $ROSETTAINPUTDIR/aat000_09_05.200_v1_3.gz

# fasta file is a file: t000_.fasta (always same name)
-in:file:fasta $ROSETTAINPUTDIR/t000_.fasta
-in:file:fullatom

-loops:frag_sizes 9 3 1
# these are the same as above (always same name)
-loops:frag_files $ROSETTAINPUTDIR/aat000_09_05.200_v1_3.gz $ROSETTAINPUTDIR/aat000_03_05.200_v1_3.gz none



# file is also a file: t000_.psipred_ss2 (always same name)
-in:file:psipred_ss2 $ROSETTAINPUTDIR/t000_.psipred_ss2
-in:file:fullatom

-idealize_after_loop_close
-out:file:silent_struct_type binary
-out:file:silent $ROSETTAOUT
-out:nstruct 10

-loops:extended
-loops:build_initial
-loops:remodel quick_ccd
-loops:relax relax
-relax:fast
-relax:default_repeats 2

-silent_decoytime

-random_grow_loops_by 4
-select_best_loop_from 1

-in:detect_disulf false
-fail_on_bad_hbond false
# Not the same name, use all => as cmdlinearg
#-in:file:template_pdb 1c4oA.pdb 1d2mA.pdb 1d9zA.pdb 1t5lB.pdb 2d7dA.pdb 2fdcB.pdb 2nmvA.pdb 2q3fA.pdb 3lluA.pdb

-bGDT
-evaluation:gdtmm      
        """        
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info        
    
