'''
Created on Oct 24, 2012

@author: lorenz
'''
from applicake.framework.interfaces import IWrapper
from applicake.framework.informationhandler import BasicInformationHandler

class mProphet(IWrapper):
    def prepare_run(self,info,log):
		
        command = 'R --slave --args bin_dir=/cluster/apps/openms/openswath-testing/mapdiv/scripts/mProphet/ ' \
                  'mquest=${file_basename}_combined.short_format.csv workflow=LABEL_FREE num_xval=$mpr_num_xval ' \
				  'run_log=FALSE write_classifier=0 write_all_pg=$writeallpg=1 help=0 project=${file_basename}_mprophet' \
				  '< /cluster/apps/openms/openswath-testing/mapdiv/scripts/mProphet/mProphet.R > ${file_basename}_mprophet.mProphet'
        return (command,info)

    def set_args(self,log,args_handler):
        """
        See interface
        """
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        return 0,info
