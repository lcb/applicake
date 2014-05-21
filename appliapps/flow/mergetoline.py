#!/usr/bin/env python
import shutil
if __name__ == "__main__":
    #merges input.ini to one line (for guse conditional execution check) and copies input to output
    merge = open('input.ini').read().replace('\n', '')
    print merge
    open('merge.ini','w').write(merge)
    shutil.copy("input.ini","output.ini")