#!/usr/bin/env python
# encoding: utf-8
# 2014-08-02 15:12:05.133992

import os
import json
import hashlib

ddir = 'data_pages'


def main():
    fdata = os.path.join(ddir, 'file_list.json')
    fdata = json.loads(open(fdata, 'r').read())

    for fld in fdata['file_list']:
        fd = open(os.path.join(ddir, fld['file_name']), 'r+b')
        h = hashlib.sha256()
        h.update(fd.read())
        if h.hexdigest() != fld['sha256']:
            raise Exception("Invalid hash %s for %s" % (h.hexdigest(), fld['file_name']))
        print("Valid hash %s for %s" % (h.hexdigest(), fld['file_name']))
# main()


if __name__ == '__main__':
    main()
