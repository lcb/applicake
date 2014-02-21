#!/usr/bin/env python
"""
Created on Mar 28, 2012

@author: quandtan
"""
import os
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils


class Apms(IWrapper):

    def prepare_run(self, info, log):
        wd = info[Keys.WORKDIR]
        csv = os.path.join(wd,'pepxml2csv.csv')
        os.symlink(info['PEPCSV'],csv)
        assoc = os.path.join(wd,'assoc.txt')
        os.symlink(info['ASSOC_FILE'],assoc)
        fasta = os.path.join(wd,'fasta.fasta')
        os.symlink(info['DBASE'],fasta)

        info['APMS_OUT'] = []
        for i in ['comppass','gfpratio','merged']:
            info['APMS_OUT'].append(os.path.join(wd,'iaLFQ_%s.csv'%i))
        return 'cd %s && %s pepxml2csv.csv assoc.txt fasta.fasta %s %s %s' % (wd,info['PREFIX'], info[Keys.IPROBABILITY],info['COMPPASS_CONFIDENCE']), info

    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, Keys.PREFIX, 'executable', default="alfq.R")
        args_handler.add_app_args(log, 'DBASE', 'fasta dbase')
        args_handler.add_app_args(log, 'ASSOC_FILE', 'assoc table')
        args_handler.add_app_args(log, 'PEPCSV', 'pepxml2csv')
        args_handler.add_app_args(log, Keys.IPROBABILITY, 'iprob',default='0.9')
        args_handler.add_app_args(log, 'COMPPASS_CONFIDENCE', 'confidence',default='0.95')

        args_handler.add_app_args(log, Keys.WORKDIR, 'wd')


        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        if run_code != 0:
            return run_code, info

        for i in info['APMS_OUT']:
            if not FileUtils.is_valid_file(log, i):
                return 1, info

        return run_code, info
