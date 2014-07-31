#!/usr/bin/env python
# encoding: utf-8
# 2014-07-31 10:58:58.552991


import hashlib
import os


def touchopen(fname, *args, **kwargs):
    fd = os.open(fname, os.O_RDWR | os.O_CREAT | os.O_TRUNC)
    return os.fdopen(fd, *args, **kwargs)
# touchopen()


def main():
    start_bytes = 1024
    end_bytes = 10 * 1024 * 1024  # 10 MB
    # end_bytes = 10 * 1024  # 10 KB
    skip_bytes = 1024
    out_dir = 'data_pages'

    try:
        os.makedirs(out_dir)
    except FileExistsError:
        pass

    for blen in range(start_bytes, end_bytes + 1, skip_bytes):
        fname = "%s.txt" % blen
        fname = os.path.join(out_dir, fname)
        # print("FNAME", blen, fname)

        with touchopen(fname, 'r+b') as fd:
            fd.write(os.urandom(blen))
            # fd.seek(0)
            h = hashlib.sha256()
            h.update(fd.read(blen))
            digest = h.digest()
            # print("DIGEST", len(digest), digest)
            fd.write(b'\x0D' + bytes(digest))

        print("FNAME {}:{}".format(fname, os.path.getsize(fname)))
        if os.path.getsize(fname) != blen + 33:
            raise Exception("Invalid file length")
    # end for blen in range(start_bytes, end_bytes + 1)
# main()


if __name__ == '__main__':
    main()
