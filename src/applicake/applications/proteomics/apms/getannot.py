#!/usr/bin/env python

import jsonrpclib,os
from applicake.framework.interfaces import IApplication
from applicake.framework.keys import Keys

#sample	uniprotID	control(bool)	treatment concat. (biol cond.)

class GetAnnotations(IApplication):

    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, Keys.WORKDIR, 'wd')
        args_handler.add_app_args(log, 'PEPCSV', 'pepcsv for samples')


        return args_handler

    def main(self, info, log):

        sample_assoc = self.get_sample_assoc()
        used_samples = self.get_samples_from_csv(info['PEPCSV'])


        info['ASSOC_FILE'] = os.path.join(info['WORKDIR'],"assoc.txt")
        with open(info['ASSOC_FILE'],"w") as assoc:
            for sample in used_samples:
                if not sample in sample_assoc:
                    log.error("No APMS annotation found for "+sample)
                    return 1,info
                else:
                    assoc.write(sample_assoc[sample]+"\n")

        return 0,info


    def get_sample_assoc(self):
        server = jsonrpclib.Server('https://ra-openbis.ethz.ch:8443/openbis/openbis/rmi-query-v1.json')
        sessionToken = server.tryToAuthenticateAtQueryServer("p-grade", "s$fh63bw*(62h")

        #find required query ID
        queries = server.listQueries(sessionToken)
        for q in queries:
            if q["name"] == 'BIOL_APMS Samples plus Conditions':
                id = q["id"]

        #execute query, gives back a dictionary where key 'rows' is interesting
        report = server.executeQuery(sessionToken, id, {})
        smplcode_assocline = {}
        for entry in report["rows"]:
            #each row is stored as list of dictionaries, where only the "values" of the dicts are interesting
            #0 DATASET_CODE,1 APMS,2 MS-Injection,3 Bait,4 Uniprot ID,5 Name,6 Condition Type,7 Condition Desc,
            #8 Condition Value,9 Condition Code
            cleandlst = []
            for listitem in entry:
                ascii = listitem["value"].encode('ascii', 'ignore')
                cleandlst.append(ascii)
            smplcode_assocline[cleandlst[2]] = "%s\t%s\t%s_%s"%(cleandlst[2], cleandlst[4] , cleandlst[5], cleandlst[9])
        server.logout(sessionToken)

        return smplcode_assocline

    def get_samples_from_csv(self,csv):
        f = open(csv)
        #skip header
        f.readline()
        samples = []
        for line in f.readlines():
            sample = line.split("\t")[1].split("~")[0]
            if not sample in samples:
                samples.append(sample)

        return samples