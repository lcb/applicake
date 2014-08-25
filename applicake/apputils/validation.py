import os
from xml.parsers import expat


def check_exitcode(log, exit_code):
    if exit_code == 0:
        log.debug("Exit code OK (0)")
    else:
        raise RuntimeError("Bad exit code (%d)" % exit_code)


def check_stdout(log, stdout):
    for line in stdout.splitlines():
        if any(x in line for x in ["Disk quota exceeded"]):
            raise RuntimeError("Job ran out of scratch space! Please remove old workflow files! (%s)" % line.strip())
        if any(x in line for x in ["std::bad_alloc", "MemoryError"]):
            raise RuntimeError("The job run out of RAM! Ask admin to increase it! (%s)!" % line.strip())
        if any(x in line for x in ["Exception:",  "IOError"]):
            raise RuntimeError("Found error keyword! Please check stdout for more details! (%s)" % line.strip())
    log.debug("No known error message in stdout")


def check_file(log, path):
    if not os.path.exists(path):
        raise RuntimeError('path [%s] does not exist' % path)
    if not os.path.isfile(path):
        raise RuntimeError('path [%s] is no file' % path)
    if not os.access(path, os.R_OK):
        raise RuntimeError('file [%s] cannot be read' % path)
    if not (os.path.getsize(path) > 0):
        raise RuntimeError('file [%s] is 0KB' % path)
    else:
        log.debug('file [%s] checked successfully' % path)


def check_xml(log, path):
    check_file(log, path)
    try:
        parser = expat.ParserCreate()
        parser.ParseFile(open(path, "r"))
    except Exception, e:
        raise RuntimeError("Invalid XML [%s]: %s" % (path, e.message))