#!/bin/bash

export ROOT=/IMSB/users/schmide/dssn
export LIB=$ROOT/lib
export BIN=$ROOT/bin
export MOD=$ROOT/mod

#export JYTHONPATH=$MOD:$JYTHONPATH

jython -Dpython.path=$LIB/cisd-base.jar:$LIB/commons-codec.jar:$LIB/commons-httpclient.jar:$LIB/commons-logging.jar:$LIB/raw-data-api.jar:$LIB/spring.jar:$LIB/src.zip:$LIB/stream-supporting-httpinvoker.jar:$MOD $BIN/dsscall.py $@
