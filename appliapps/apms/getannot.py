#!/usr/bin/env python

import os
import subprocess

import jsonrpclib

from applicake.app import BasicApp
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class GetAnnotations(BasicApp):
    def add_args(self):
        return [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument('PEPCSV', 'pepcsv for samples')
        ]

    def run(self, log, info):
        sample_assoc = self.get_sample_assoc()
        used_samples = self.get_samples_from_csv(info['PEPCSV'])

        info['ASSOC_FILE'] = os.path.join(info[Keys.WORKDIR], "assoc.txt")
        with open(info['ASSOC_FILE'], "w") as assoc:
            for sample in used_samples:
                if not sample in sample_assoc:
                    log.error("No APMS annotation found for " + sample)
                    return 1, info
                else:
                    assoc.write(sample_assoc[sample] + "\n")

        return info

    def get_sample_assoc(self):
        server = jsonrpclib.Server('https://ra-openbis.ethz.ch:8443/openbis/openbis/rmi-query-v1.json')
        pwd = subprocess.check_output("konk p-grade", shell=True).strip()
        sessionToken = server.tryToAuthenticateAtQueryServer("p-grade", pwd)

        #find required query ID
        queries = server.listQueries(sessionToken)
        for q in queries:
            if q["name"] == 'BIOL_APMS mini table':
                id = q["id"]


        #execute query, gives back a dictionary where key 'rows' is interesting
        report = server.executeQuery(sessionToken, id, {})
        smplcode_assocline = {}
        for entry in report["rows"]:
            #each row is stored as list of dictionaries, where only the "values" of the dicts are interesting
            #0 msinjection,1 uniprotid,2 name,3 iscontrol
            cleandlst = []
            for listitem in entry:
                ascii = listitem["value"].encode('ascii', 'ignore')
                cleandlst.append(ascii)
            if "YES" in cleandlst[3] or "TRUE" in cleandlst[3]:
                smplcode_assocline[cleandlst[0]] = "%s\tcontrolrun\t%s" % (cleandlst[0], cleandlst[2])
            else:
                smplcode_assocline[cleandlst[0]] = "%s\t%s\t%s" % (cleandlst[0], cleandlst[1], cleandlst[2])
        server.logout(sessionToken)

        return smplcode_assocline

    def get_samples_from_csv(self, csv):
        f = open(csv)
        #skip header
        f.readline()
        samples = []
        for line in f.readlines():
            sample = line.split("\t")[1].split("~")[0]
            if not sample in samples:
                samples.append(sample)

        return samples


if __name__ == "__main__":
    GetAnnotations.main()