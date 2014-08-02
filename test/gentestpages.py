#!/usr/bin/env python
# encoding: utf-8
# 2014-07-31 10:58:58.552991

"""
8B 16B 32B 64B 128B 256B 512B 768B
1KB 2KB 3KB 4KB 5KB 6KB 7KB 8KB 9KB 
10KB 20KB 30KB 40KB 50KB 60KB 70KB 80KB 90KB 
100KB 200KB 300KB 400KB 500KB 600KB 700KB 800KB 900KB 
1MB 2MB 3MB 4MB 5MB 6MB 7MB 8MB 9MB 
10MB 20MB 30MB 40MB 50MB 60MB 70MB 80MB 90MB 100MB
"""


import hashlib
import os
import json
import datetime

FMAPS = [
    {
        'list': [8, 16, 32, 64, 128, 256, 768],
    },
    {
        'start': 1024,
        # 'skip': 1024, #  if skip is not same as start, set skip
        'num': 9,
    },
    {
        'start': 1024 * 10,
        'num': 9,
    },
    {
        'start': 1024 * 100,
        'num': 9,
    },
    {
        'start': 1024 * 1024,
        'num': 9,
    },
    {
        'start': 1024 * 1024 * 10,
        'num': 10,
    },
]


def touchopen(fname, *args, **kwargs):
    fd = os.open(fname, os.O_RDWR | os.O_CREAT | os.O_TRUNC)
    return os.fdopen(fd, *args, **kwargs)
# touchopen()


def write_bytes(num_bytes, fbase):
    print("write_bytes", num_bytes, fbase)

    fn = "%s.txt" % num_bytes
    fname = os.path.join(fbase, fn)
    digest = ''

    with touchopen(fname, 'r+b') as fd:
        rbytes = os.urandom(num_bytes)
        fd.write(rbytes)
        h = hashlib.sha256()
        h.update(rbytes)
        digest = h.hexdigest()

    if os.path.getsize(fname) != num_bytes:
        raise Exception("Invalid file length")

    return {'file_name': fn, 'sha256': digest}
# write_bytes()


def write_skipped(fmap, fbase):
    start = fmap['start']
    skip = fmap.get('skip', start)
    stop = start * (fmap['num'] + 1)

    result_list = []
    for blen in range(start, stop, skip):
        result_list.append(write_bytes(blen, fbase))
    # end for blen in range(fmap['start'], )

    return result_list
# write_skipped()


def write_listed(fmap, fbase):
    result_list = []
    for blen in fmap['list']:
        result_list.append(write_bytes(blen, fbase))
    # end for blen in fmap['list']

    return result_list
# write_listed()


def main():
    out_dir = 'data_pages'

    try:
        os.makedirs(out_dir)
    except FileExistsError:
        pass

    result_list = []
    for fmap in FMAPS:
        if 'list' in fmap:
            result_list += write_listed(fmap, out_dir)
        elif 'start' in fmap:
            result_list += write_skipped(fmap, out_dir)
        else:
            raise Exception("Bad file map %s" % fmap)

    fname = os.path.join(out_dir, 'file_list.json')
    file_data = {
        'timestamp': datetime.datetime.now().isoformat(),
        'file_list': result_list,
    }

    with open(fname, 'w') as fd:
        fd.write(json.dumps(file_data, sort_keys=True, indent=2))
    # end for fmap in FMAPS
# main()


if __name__ == '__main__':
    main()
