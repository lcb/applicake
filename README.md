[![Build Status](https://travis-ci.org/lcb/applicake.svg)](https://travis-ci.org/lcb/applicake)
[![Project Stats](https://www.openhub.net/p/applicake/widgets/project_thin_badge.gif)](https://www.openhub.net/p/applicake)

# About

Applicake was developed as part of the SCI-BUS project. The basic idea is to wrap 3rd-party tools into "Applicake apps" to get uniform parameter parsing, tool execution, error handling and logging.

Applicake apps are particularly useful in combination with workflow engines for executing sequences of heterogeneous tools. For flow control workflow engines often rely on uniform exit codes or error messages within the nodes. Applicake provides an additional layer of abstraction to develop standardized workflow nodes, to simplify diverse tools to a streamlined workflow.
Related software

Applicake is geared towards wrapping sequences of tools. To wrap a single command line tool pyCLI might be an alternative solution. If you need a complete workflow manager, have a look at ruffus or gUSE.

## Related Projects
https://github.com/iracooke/protk

# Howto

## Install
Go to the folder where you want to install applicake
$ cd /install_dir/

make applicake available to your python environment by adding the root folder to your pytonpath
$ vim ~/.bashrc
export PYTHONPATH=/install_dir/applicake-master/applicake/:/install_dir/applicake-master/appliapps/:$PYTHONPATH

for testing sucessful install try
$ /install_dir/applicake-master/executables/ruffus/echoWF.py

for testing sucessful install try
python.exe .\appliapps\examples\cp.py --FILE "test"

## Development Overview

The following steps are done when an appliapp is run:

1. The list of required parameters/arguments is assembled
1. The command line arguments are parsed
1. If requested, additional parameters are read from set INPUT infofile
1. Logging is set up
1. If requested a working directory is created
1. The appliapp is executed (run)
1. If requested, the parameters are written to set OUTPUT file (can be used for a next app)

For a regular appliapp only steps 1. and 6. have to be defined, the rest is done in the framework. How this is done see next paragraph.

## Basic development
### BasicApp

For simply wrapping some python code into an appliapp derive a class from `applicake.app.BasicApp` and implement the `add_args` and `run` methods

``` 
class PythonEcho(BasicApp): 
def add_args(self): 
    return [ Argument("COMMENT", "String to be displayed") ]

def run(self, log, info):
    print info["COMMENT"]
    return info
``` 
As you can see from the example above the parameters required from command line or the config file must be defined as a list of Argument instances in the add_args method. In the run method these can be accessed with the info dictionary.

### WrappedApp
To wrap an external tool there is the framework class `applicake.app.WrappedApp` (which is derived from BasicApp) but splits up the run method into three steps: 

1. prepare_run 
2. (execute_run) 
3. validate_run 

The basic idea is that in the `prepare_run` method the command line to run is assembled. `execute_run` spawns a subprocess, and `validate_run` checks if the run was valid. The default `execute_run` and `validate_run` methods are made so that they need not to be overwritten by default. Consequently, for a minimal appliapp it is sufficient to implement the `prepare_run` method, along with the `add_args` method:

``` 
class ExternalEcho(WrappedApp): 
    def add_args(self): 
        return [ 
            Argument(Keys.EXECUTABLE, KeyHelp.EXECUTABLE, default="echo"),
            Argument("COMMENT", "String to be displayed", default="default comment") 
        ]

def prepare_run(self, log, info):
    exe = info["EXECUTABLE"]
    comment = info["COMMENT"]
    command = "%s %s" % (exe, comment)
    return info, command
``` 
As you can see from the example above the `prepare_run` method return the updated info object and the command line to run.

### Run an app

To actually run the class call its main method, like for example: 
```
if __name__ == "__main__": 
    Echo.main() 
```
If more influence is needed (especially to the validation) see section below.

## Extended development
### args

The arguments used by the app should be defined as a list of Argument instances. 
```
def add_args(): 
    return [ 
        Argument("COMMENT","comment to use"), 
        Argument("EXECUTABLE","executable to use",default="/bin/true") 
    ] 
```
The constructor of Argument takes first the name of the parameter, second the helptext associated with the parameter, and third the optional keyword argument "default". The helptext is displayed when calling the app with "-h". The default value is only used when this argument was neither specified on the command line nor in the INPUT infofile (see below).

### Logging
The appliapps have a logger accessible. It works like a normal python logger. The arguments "LOG_LEVEL" and influence its behaviour.

### Temporary folders
In applicake there is a integrated system to create temporary working directories in a convenient way, the resulting folder structure is also easy to debug. For making automatically a unique "logical" workdir set the WORKDIR argument to the app, the dir will be stored there 

```
class Echo(BasicApp): 
def add_args(): 
    return [ Argument('WORKDIR','make wd') ] 
def prepare_run(): 
    info['WORKDIR']
```

### Validate execution

The default `validate_run` method checks if the exit code was 0 and no text "Exception" was found in stdout, which is usually sufficient for a correctly written 3rd party tool. However, in real life tools can have exit code 0 even on failures or produce cryptic error messages. Thus it is recommended to add app specific validation code which produces more clear messages than the default "Exit code not 0". There are some validation methods readily avaiable in `applicake.coreutils.validation`. Some example validation code: 

```
def validate_run(self, log, info, exit_code, stdout): 
    if "out of mem" in stdout: 
        raise Exception("Ran out of memory") 
    if exit_code != 0: 
        raise Exception("Exitcode was not 0") 
    if not validation.check_xml(info["MZML"]): 
        raise Exception("Output file not valid")
```

## Available Appliapps
### Examples
For beginners it is strongly recommended to have a look at the example apps.

### Flow
A particular tricky task in workflow handling is branching and merging. Therefore the appliapp package flow was created to provide some solid default branching/merging handling implementations.