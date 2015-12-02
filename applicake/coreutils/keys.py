class Keys(object):
    """
    Some keys commonly used by the framework
    """

    INPUT = 'INPUT'  #volatile
    OUTPUT = 'OUTPUT'  #volatile
    LOG_LEVEL = 'LOG_LEVEL'
    WORKDIR = 'WORKDIR'  #volatile
    BASEDIR = 'BASEDIR'
    JOB_ID = 'JOB_ID'
    NAME = 'NAME'  #volatile
    ALL_ARGS = 'ALL_ARGS'

    #flow args
    BRANCH = 'BRANCH'  #volatile
    COLLATE = 'COLLATE'  #volatile
    SPLIT = 'SPLIT'  #volatile
    SPLIT_KEY = 'SPLIT_KEY'  #volatile
    MERGE = 'MERGE'  #volatile
    MERGED = 'MERGED'  #volatile
    SUBJOBLIST = 'SUBJOBLIST'
    SUBJOBSEP = "|"

    #other frequent apps keys
    MODULE = 'MODULE'
    EXECUTABLE = 'EXECUTABLE'
    THREADS = 'THREADS'
    DATASET_CODE = 'DATASET_CODE'
    MZXML = 'MZXML'
    PEPXML = 'PEPXML'
    PROTXML = 'PROTXML'
    PEPTIDEFDR = 'PEPTIDEFDR'


class KeyHelp(object):
    """
    Help texts for the common keys
    """
    INPUT = 'Input config file location (volatile argument)'
    OUTPUT = 'Output config file location (volatile argument)'
    LOG_LEVEL = "Logging level (CRITICAL, ERROR, WARNING, INFO or DEBUG)"
    BASEDIR = "`-> Root directory for making workdir paths"
    JOB_ID = '`-> Unique job ID for making workdir paths. If none is specified one is generated in ' + Keys.BASEDIR
    SUBJOBLIST = "`-> List of subjobs IDs for making workdir paths. Managed by flow apps, do not modify"
    NAME = '`-> (App)name for making workdir paths (volatile argument)'
    WORKDIR = 'Directory to put output files to. If none is specified one is created ' \
              '(using %s, %s, %s and %s)' % (Keys.BASEDIR, Keys.JOB_ID, Keys.SUBJOBLIST, Keys.NAME)
    MODULE = "Allows loading a module before executing external command, for WrappedApps. " \
             "Requires http://modules.sourceforge.net/ installation."
    ALL_ARGS = 'Special argument to give entire info object to app. Useful for dropbox or flow apps (volatile argument)'

    BRANCH = 'File names for branched output config files (volatile argument)'
    COLLATE = 'File names for input config files to collate (volatile argument)'
    SPLIT = 'Basename for split output config files (volatile argument)'
    SPLIT_KEY = 'Key which is used for splitting uf the input config file (volatile argument)'
    MERGE = 'Basenames for input config files to merge (volatile argument)'
    MERGED = 'Basename for merged output config files (volatile argument)'


    EXECUTABLE = "Echo executable to be run (volatile argument)"
    EXECDIR = "Executable directory location"
    THREADS = "Number of threads/processors to be used"
    DATASET_CODE = ''
    MZXML = ''
    PEPXML = ''
    PROTXML = ''
    PEPTIDEFDR = ''
