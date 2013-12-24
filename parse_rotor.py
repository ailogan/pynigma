#!/usr/bin/python

import sys

line = sys.stdin.readline()[:-1]

current_char = 'A'

for char in line:
    print current_char + "=" + char
    current_char = chr(ord(current_char)+1)


