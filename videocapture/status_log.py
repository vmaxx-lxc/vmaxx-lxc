#! /usr/bin/python
#
# record running status into log.txt. 
# send Email every 5 mins
#
# code by Ruoyu Yang
# 2017 08 20
#

import sys
import os
import fcntl

[content] = sys.argv[1:]
f = open('status_log.txt', 'a+')

fcntl.flock(f,fcntl.LOCK_EX)####

f.write(content)
f.write('\n')

fcntl.flock(f,fcntl.LOCK_UN)####
f.close()

