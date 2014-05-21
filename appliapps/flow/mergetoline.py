#!/usr/bin/env python
import shutil
from applicake.app import BasicApp


class MergeToLine(BasicApp):
    @classmethod
    def main(cls):
        #merges input.ini to one line (for guse conditional execution check) and copies input to output
        merge = open('input.ini').read().replace('\n', '')
        print merge
        open('merge.ini','w').write(merge)
        shutil.copy("input.ini","output.ini")