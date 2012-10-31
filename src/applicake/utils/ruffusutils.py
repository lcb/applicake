'''
Created on Aug 17, 2012

@author: lorenz

'''

from applicake.framework.interfaces import IApplication, IWrapper
from applicake.framework.runner import ApplicationRunner, WrapperRunner, IniFileRunner, CollectorRunner, IniFileRunner2
from applicake.applications.commons.generator import Generator
from applicake.applications.commons.collector import BasicCollector
from applicake.applications.commons.inifile import Unifier



def WrapApp(applic, input_file_name, output_file_name, opts=None):
    argv = ['fakename.py', '-i', input_file_name, '-o', output_file_name]
    if opts is not None:
        argv.extend(opts)
    
    application = applic()
    
    if isinstance(application, Generator):
        runner = IniFileRunner()
        argv.remove('-o')
        argv.remove('')
    elif isinstance(application, BasicCollector):
        runner = CollectorRunner()
        argv.remove('-i')
        argv.remove('')
    elif isinstance(application, Unifier):
        runner = IniFileRunner2()
    elif isinstance(application, IApplication):
        runner = ApplicationRunner()
    elif isinstance(application, IWrapper):
        runner = WrapperRunner()
    else:
        raise Exception('could not identfy runner for application [%s]' % applic.__name__)   
     
    exit_code = runner(argv, application)
    if exit_code != 0:
        raise Exception("[%s] failed with exitcode [%s]" % (applic.__name__, exit_code))
