#!/usr/bin/env python
import csv

precision = 6

def get_iprob_for_fdr(requested_fdr, tool_type, mayuout=None, pepxml=None):
    """
    Retrieves interprophet_probability corresponding requested fdr&type

    :param requested_fdr: 0-1 (=0-100%)
    :param tool_type: one of iprophet-pepFDR iprophet-iprob mayu-mFDR mayu-pepFDR mayu-protFDR
    :param mayuout: needed if mayu-* fdr type requested
    :param pepxml: needed if iprophet-* fdr type requested
    :return: float iprob, str nicely formatted fdr string and iprob mapping
    """

    requested_fdr = float(requested_fdr)
    tool, type = tool_type.split("-")

    if tool == "iprophet":
        iprob, effective_fdr = _get_iprob_for_fdr_iprophet(requested_fdr, type, pepxml)
    elif tool == "mayu":
        iprob, effective_fdr = _get_iprob_for_fdr_mayu(requested_fdr, type, mayuout)
    else:
        raise RuntimeError("Unknown tool " + tool)

    #harmonize to 6digits after comma (%g without trailing zeroes)
    iprob = round(iprob, precision)
    effective_fdr = round(effective_fdr,precision)
    fdr_str = "%g %s (=%g iprob)" % (effective_fdr, tool_type, iprob)
    print "Requested",requested_fdr,'got',fdr_str
    return iprob, fdr_str


def _get_iprob_for_fdr_iprophet(requested_fdr, type, source):
    """
    Reads out the iprob corresponding pepFDR from the iProphet header.
    If type is iprob (=dummy) input is taken 1:1
    """
    iprob = None

    if type == 'iprob':
        iprob = requested_fdr
    if type == 'pepFDR':
        for line in open(source):
            if line.startswith('<error_point error="%s' % requested_fdr):
                iprob = float(line.split(" ")[2].split("=")[1].replace('"', ''))
                break

    if not iprob:
        raise RuntimeError("No iprob found for iprophet-%s of %s" % (type, requested_fdr))
    return iprob, requested_fdr


def _get_iprob_for_fdr_mayu(requested_fdr, type, source):
    """
    Finds closest available FDR to requested one, and gives back adjusted FDR
    """
    iprob = None
    effective_fdr = None
    mindiff = 1.0
    reader = csv.DictReader(open(source, "rb"))
    for line in reader:
        linefdr = float(line[type])
        diff = abs(linefdr - requested_fdr)
        if diff < mindiff:
            mindiff = diff
            effective_fdr = linefdr
            iprob = float(line['IP/PPs'])

    #if mindiff > 0.01:
    #    raise RuntimeError("No close match found for %s mayu-%s" % (fdr, type))
    if not iprob:
        raise RuntimeError("No iprob found for %s mayu-%s" % (requested_fdr, type))
    return iprob, effective_fdr