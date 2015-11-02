import sys
from ast import literal_eval

from applicake.coreutils.keys import Keys


class Argument(object):
    def __init__(self, *args, **kwargs):
        try:
            self.name = args[0]
            self.help = args[1]
        except:
            raise Exception("Wrong initialization of Argument(name,help,**kwargs), check signature!")
        self.default = kwargs.get('default', None)
        #WORKDIR: eliminate [required] flag for WORKDIR
        if self.name in [Keys.WORKDIR,Keys.ALL_ARGS]:
            self.default = ''


def parse_sysargs(arglist):
    #helptext printing style from argparse
    if '-h' in sys.argv:
        _print_help(arglist)

    #argument parsing harmonized with Configobj
    all_args = {}
    key = None
    for sarg in sys.argv:
        if sarg.startswith("--"):
            key = sarg[2:]
        else:
            if key is None:
                continue
            if key in all_args:
                all_args[key] += " " + sarg
            else:
                all_args[key] = sarg

    for k, v in all_args.iteritems():
        try:
            all_args[k] = literal_eval(v)
        except:
            all_args[k] = v

    defaults = dict((arg.name, arg.default) for arg in arglist if arg.default is not None)
    return defaults, all_args


def _print_help(arglist):
    print "Usage:\n" \
          "  -h                     Show this help message and exit"
    for arg in arglist:
        if arg.default is None:
            deflt = "[required]"
        else:
            deflt = arg.default
        print "  --%-20s %s" % (arg.name + " " + deflt, arg.help or "")
        #prettify helptext
        if arg.name is Keys.LOG_LEVEL:
            print ""
    sys.exit(1)