#!/usr/bin/env python
from applicake.app import BasicApp
from applicake.coreutils.arguments import Argument
from applicake.coreutils.info import get_handler
from applicake.coreutils.keys import Keys, KeyHelp


class Branch(BasicApp):
    def add_args(self):
        return [
            Argument(Keys.ALL_ARGS, KeyHelp.ALL_ARGS),
            Argument(Keys.BRANCH, KeyHelp.BRANCH)
        ]

    def run(self, log, info):
        ih = get_handler(info[Keys.BRANCH])
        tobranch = info[Keys.BRANCH].split(" ")
        del info[Keys.BRANCH]
        for branch in tobranch:
            log.info("Branching " + branch)
            info = info.copy()
            ih.write(info, branch)

        return info


if __name__ == "__main__":
    Branch.main()