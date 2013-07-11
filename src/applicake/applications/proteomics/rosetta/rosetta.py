"""
Created on May 10, 2012

@author: loblum
"""

import os
from configobj import ConfigObj 
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.framework.keys import Keys


class Rosetta(IWrapper):
    """
    Wrapper for minirosetta.default.linuxgcc
    """

    def prepare_run(self, info, log):
        wd = info[Keys.WORKDIR]

        for f in info[Keys.DSSOUTPUT]:
            if "dataset.properties" in f:
                dsprop = ConfigObj(f)
        info.update(dsprop)
        
        info["PDBS"] = ""               
        for pdb in dsprop["TEMPLATES"].split():
            info["PDBS"] += info["ROSETTA_EXTRACTDIR"] + "/" + pdb + " "        

        info['ROSETTA_OUT'] = os.path.join(wd, 'default.out')
        #necessary: output is compressed by gzip
        info['ROSETTA_COMPRESSEDOUT'] = info['ROSETTA_OUT'] + '.gz'

        app_info = info.copy()
        app_info["THREEMERS"] = info["3MERS"] 
        app_info["NINEMERS"] = info["9MERS"]
        
        app_info['TEMPLATE'] = os.path.join(wd, 'flags')
        RosettaTemplate().modify_template(app_info, log)
        
        command = "%s @%s && gzip %s" % (info["PREFIX"], app_info['TEMPLATE'], app_info['ROSETTA_OUT'])
        return command, info

    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, Keys.PREFIX, 'command to execute',default="minirosetta.default.linuxgccrelease")
        args_handler.add_app_args(log, Keys.DSSOUTPUT, 'file list downloaded by dss')
        args_handler.add_app_args(log, Keys.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, 'ROSETTA_EXTRACTDIR', 'dir where rosetta dataset was extracted to')
        args_handler.add_app_args(log, 'NSTRUCT', 'Number of structures created')
        args_handler.add_app_args(log, 'RANDOM_GROW_LOOPS_BY', '')
        args_handler.add_app_args(log, 'SELECT_BEST_LOOP_FROM', '')
        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        return run_code, info


class RosettaTemplate(BasicTemplateHandler):
    def read_template(self, info, log):
        template = """
# module load rosetta (no need to specify the Rosetta database)
-run:protocol threading
-run:shuffle

# alignment.filt is an input file
-in:file:alignment $ROSETTA_EXTRACTDIR/alignment.filt
-cm:aln_format grishin

# files that start with aat000 are fragment files, 03 and 09 refers to length of fragments (always same name)
-frag3 $ROSETTA_EXTRACTDIR/$THREEMERS
-frag9 $ROSETTA_EXTRACTDIR/$NINEMERS

# fasta file is a file: t000_.fasta (always same name)
-in:file:fasta $ROSETTA_EXTRACTDIR/t000_.fasta
-in:file:fullatom

-loops:frag_sizes 9 3 1
# these are the same as above (always same name)
-loops:frag_files $ROSETTA_EXTRACTDIR/$NINEMERS $ROSETTA_EXTRACTDIR/$THREEMERS none

# file is also a file: t000_.psipred_ss2 (always same name)
-in:file:psipred_ss2 $ROSETTA_EXTRACTDIR/t000_.psipred_ss2
-in:file:fullatom

-idealize_after_loop_close
-out:file:silent_struct_type binary
-out:file:silent $ROSETTA_OUT
-out:nstruct $NSTRUCT

-loops:extended
-loops:build_initial
-loops:remodel quick_ccd
-loops:relax relax
-relax:fast
-relax:default_repeats 2

-silent_decoytime

-random_grow_loops_by $RANDOM_GROW_LOOPS_BY
-select_best_loop_from $SELECT_BEST_LOOP_FROM

-in:detect_disulf false
-fail_on_bad_hbond false
#-in:file:template_pdb 1c4oA.pdb 1d2mA.pdb 1d9zA.pdb 1t5lB.pdb 2d7dA.pdb 2fdcB.pdb 2nmvA.pdb 2q3fA.pdb 3lluA.pdb
-in:file:template_pdb $PDBS
-bGDT
-evaluation:gdtmm      
        """
        return template, info
    
