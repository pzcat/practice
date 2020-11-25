# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author PZcat created at 2019/10/7 23:16

import os
from hashlib import md5


def get_filename(filename: str) -> str:
    suffix = filename.split('.')[-1]
    m = md5(os.urandom(16)+filename.encode('utf-8'))
    return m.hexdigest() + '.' + suffix


if __name__ == '__main__':
    print(get_filename('test.txt'))