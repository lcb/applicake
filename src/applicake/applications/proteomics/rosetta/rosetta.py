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
  
    def prepare_run(self,info,log):
        wd = info[self.WORKDIR]
        info['TEMPLATE'] = os.path.join(wd,'rosetta.tpl') 
        info['ROSETTAOUT'] = os.path.join(wd,'default.out')                
        _,info = RosettaTemplate().modify_template(info, log)        
        #FIXME: template db are given  by cmdline to have correct expansion to n files 
        command = "minirosetta.default.linuxgccrelease @%s -in:file:template_pdb %s/*.pdb" %(info['TEMPLATE'],info['ROSETTAINPUTDIR']) 
        return command,info  
    
    def set_args(self,log,args_handler): 
        args_handler.add_app_args(log, 'ROSETTAINPUTDIR', 'Peak list file in mgf format')     
        args_handler.add_app_args(log, 'NSTRUCT', 'Number of structures created')     
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')  
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory') 
        return args_handler      
    
    def validate_run(self,info,log,run_code, out_stream, err_stream):
        return run_code,info  

class RosettaTemplate(BasicTemplateHandler):
    def read_template(self, info, log):
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
-out:nstruct $NSTRUCT

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
        return template,info        
    
