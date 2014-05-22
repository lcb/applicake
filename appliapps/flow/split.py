#!/usr/bin/env python
import copy

from applicake.coreutils.arguments import Argument
from applicake.coreutils.info import get_handler
from applicake.app import BasicApp
from applicake.coreutils.keys import Keys, KeyHelp


class Split(BasicApp):
    def add_args(self):
        return [
            Argument(Keys.ALL_ARGS, KeyHelp.ALL_ARGS),
            Argument(Keys.SPLIT, KeyHelp.SPLIT),
            Argument(Keys.SPLIT_KEY, KeyHelp.SPLIT_KEY)
        ]

    def run(self, log, info):
        basename = info[Keys.SPLIT]
        key = info[Keys.SPLIT_KEY]
        value = info.get(key,"")
        if not isinstance(value, list):
            value = [value]

        info = info.copy()
        del info[Keys.SPLIT]
        del info[Keys.SPLIT_KEY]

        if info.get(Keys.SUBJOBLIST, "") == "":
            info[Keys.SUBJOBLIST] = []

        for i, val in enumerate(value):
            infocopy = copy.deepcopy(info)
            infocopy[key] = val
            infocopy[Keys.SUBJOBLIST].append("%s%s%d%s%d" % (key, Keys.SUBJOBSEP, i, Keys.SUBJOBSEP, len(value)))
            path = basename + "_" + str(i)
            log.debug("Writing split file " + path)
            get_handler(basename).write(infocopy, path)

        return info


if __name__ == "__main__":
    Split.main()