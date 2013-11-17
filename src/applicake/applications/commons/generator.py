"""
Created on Mar 20, 2012

@author: quandtan
"""

from applicake.framework.keys import Keys
from applicake.framework.interfaces import IApplication
from applicake.utils.sequenceutils import SequenceUtils
from applicake.utils.dictutils import DictUtils
from applicake.framework.informationhandler import IniInformationHandler


class IniGenerator(IApplication):
    """   
    A basic Generator creates all possible value combinations from the input file if it contains keys with multiple values.
    The results are stored in files which are named in dependency input file name and the pattern accepted 
    by the applied worklfow manager.
    Ini file dependent because of BasicInformaitonHandler()
    """

    def write_files(self, info, log, dicts, idx_sep='_'):
        """
        Generates ini files from a list of dictionaries
        
        @type info: dict 
        @param info: Dictionary with information about the application.
        @type dicts: List of dicts
        @type dicts: List of dictionaries used to create ini files
        """

        for idx, dic in enumerate(dicts):
            log.debug('dict to write: [%s]' % dic)
            path = "%s%s%s" % (dic[Keys.GENERATOR], idx_sep, idx)
            log.debug(path)
            dic[Keys.OUTPUT] = path
            dic[Keys.GENERATOR_CHECKSUM] = len(dicts)
            IniInformationHandler().write_info(dic, log)
            log.debug('create file [%s]' % path)
        return info


class IniDatasetcodeGenerator(IniGenerator):
    """
    Generator that rely on the existence of a specific dataset-code key that is retrieved from an OpenBIS instance.
    
    The generator splits the input file by the all possible parameter combinations and then by all defined dataset-codes.
    """


    def main(self, info, log):
        """
        Generate the cartesian product of all values from info and writes them to files.

        There is a distinction between dataset codes and parameters. For every parameter combination
        a new key [PARAM_IDX] is added. Dataset combinations are indexed using another key [DATASET_CODE].

        @precondition: 'info' object has to contain key [DATASET_CODE]
        @type info: see super class
        @param info: see super class
        @type log: see super class
        @param log: see super class
        """
        #TODO: simplify "wholeinfo" apps
        #re-read INPUT to get access to whole info, needs set_args(INPUT). add runnerargs to set_args if modified by runner
        ini = IniInformationHandler().get_info(log, info)
        basedic = DictUtils.merge(log, info, ini)

        if "COMMENT" in info:
            info["COMMENT"] = str(info["COMMENT"]).replace(",","_")

        #check if value DATASE_CODE is defined as list
        dsc = basedic[Keys.DATASET_CODE]
        if not isinstance(dsc, list):
            log.debug('found value of [%s] not to be a list [%s], converting it' % (Keys.DATASET_CODE, dsc))
            basedic[Keys.DATASET_CODE] = [dsc]
        log.debug('need to remove some keys from the work copy for a "clean" start ;-)')
        remove_keys = [Keys.NAME]
        for key in remove_keys:
            try:
                del basedic[key]
                log.debug('removed key [%s] from work copy' % key)
            except:
                log.debug('work copy did not have key [%s]' % key)
                # prepare first the product of a parameter combinations
        escape_keys = [Keys.DATASET_CODE]
        param_dicts = DictUtils.get_product_dicts(basedic, log, escape_keys, idx_key=Keys.PARAM_IDX)
        log.debug('param_dicts: [%s]' % param_dicts)
        log.debug('created [%s] dictionaries based on parameter combinations' % len(param_dicts))
        # prepare combinations based on files
        param_file_dicts = []
        escape_keys = []
        for dic in param_dicts:
            file_dicts = DictUtils.get_product_dicts(dic, log, escape_keys, idx_key=Keys.FILE_IDX)
            param_file_dicts.extend(file_dicts)

        log.debug('created [%s] dictionaries based on parameter and file combinations' % len(param_file_dicts))
        # write ini files
        self.write_files(info, log, param_file_dicts)
        return 0, info

    def set_args(self, log, args_handler):
        """
        See interface
        """
        args_handler.add_app_args(log, Keys.GENERATOR,
                                  'Base name for generating output files (such as for a parameter sweep)',
                                  action='append')

        #TODO: simplify "wholeinfo" apps
        args_handler.add_app_args(log, Keys.INPUT, 're-read input to access whole info')
        args_handler.add_app_args(log, Keys.BASEDIR, 'get basedir if set or modified by runner')
        args_handler.add_app_args(log, Keys.JOB_IDX, 'get jobidx if set or modified by runner')
        args_handler.add_app_args(log, Keys.STORAGE, 'get storage if set or modified by runner')
        args_handler.add_app_args(log, Keys.LOG_LEVEL, 'get loglevel if set or modified by runner')

        return args_handler


class IniParametersetGenerator(IniGenerator):
    """
    Generator that runs after a collector to split the information by the parameter sets.
    """

    def main(self, info, log):
        """
        Generate the cartesian product of all values from info and writes them to files. 
        
        There is a distinction between dataset codes and parameters. For every parameter combination
        a new key [%s] is added. Dataset combinations are indexed using another key [%s]. 
        
        @precondition: 'info' object has to contain key [%s]
        @type info: see super class
        @param info: see super class
        @type log: see super class
        @param log: see super class 
        """

        #TODO: simplify "wholeinfo" apps
        #re-read INPUT to get access to whole info, needs set_args(INPUT). add runnerargs to set_args if modified by runner
        ini = IniInformationHandler().get_info(log, info)
        basedic = DictUtils.merge(log, info, ini)

        if not isinstance(basedic[Keys.PARAM_IDX], list):
            log.info('value [%s] of key [%s] was no list, converting' % (basedic[Keys.PARAM_IDX], Keys.PARAM_IDX))
            basedic[Keys.PARAM_IDX] = [basedic[Keys.PARAM_IDX]]
            #return 1,info

        #remove file_idx as it is not longer needed
        basedic = basedic.copy()
        del basedic[Keys.FILE_IDX]
        param_dicts = []
        if len(SequenceUtils.unify(basedic[Keys.PARAM_IDX], reduce=True)) == 1:
            for key in basedic.keys():
                if isinstance(basedic[key], list) and key != Keys.INPUT:
                    basedic[key] = SequenceUtils.unify(basedic[key], reduce=True)
            param_dicts.append(basedic)
        else:
            keys = basedic.keys()
            log.debug('number of keys [%s]' % len(keys))
            param_idxs = basedic[Keys.PARAM_IDX]
            # loops of unique list of found parameter idices
            for param_idx in SequenceUtils.unify(param_idxs):
                param_dict = {}
                # gets the positions in the value list of the key
                log.debug('process parameter index [%s]' % param_idx)
                positions = SequenceUtils.get_indices(param_idxs, lambda x: x == param_idx)
                log.debug('found it at positions [%s] in original array [%s]' % (positions, basedic[Keys.PARAM_IDX]))
                # extracts for every key of the info object the values that match these positions
                # and writes them into a new dictionary
                log.debug('start splitting values for every key in info object')
                for key in keys:
                    value = basedic[key]
                    #log.debug('value [%s] for key [%s]' % (value,key)) 
                    if not isinstance(value, list):
                        log.info('found value %s is not a list' % value)
                        param_dict[key] = value
                    elif len(value) != len(param_idxs):
                        log.info(
                            'length of key %s [%s] does not correspond to length of param indices [%s]. key possibly not coming from input file' % (
                            key, len(value), len(param_idxs)))
                        param_dict[key] = SequenceUtils.unify(value, reduce=True)
                    else:
                        values = [value[pos] for pos in positions]
                        param_dict[key] = SequenceUtils.unify(values, reduce=True)
                log.debug('param idx [%s] created dict [%s]' % (param_idx, param_dict))
                param_dicts.append(param_dict)
                # write ini files
        self.write_files(basedic, log, param_dicts)
        return 0, info


    def set_args(self, log, args_handler):
        """
        See interface
        """
        args_handler.add_app_args(log, Keys.GENERATOR,
                                  'Base name for generating output files (such as for a parameter sweep)',
                                  action='append')

        #TODO: simplify "wholeinfo" apps
        args_handler.add_app_args(log, Keys.INPUT, 're-read input to access whole info')
        args_handler.add_app_args(log, Keys.BASEDIR, 'get basedir if set or modified by runner')
        args_handler.add_app_args(log, Keys.JOB_IDX, 'get jobidx if set or modified by runner')
        args_handler.add_app_args(log, Keys.STORAGE, 'get storage if set or modified by runner')
        args_handler.add_app_args(log, Keys.LOG_LEVEL, 'get loglevel if set or modified by runner')

        return args_handler     
