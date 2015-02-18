#!/usr/bin/python2
import fileinput, glob, string, sys, os
from os.path import join
import shutil

sourcepath = "../Mods/*"
destpath = "../dist/Mods/"

sourcefiles = glob.glob(sourcepath)
print "Sourcefiles {}".format(sourcefiles)
for srcfile in sourcefiles:
    shutil.copy(srcfile,destpath)


stext = "from colorview2d "
rtext = ""

print "finding: " + stext + " replacing with: " + rtext + " in: " + destpath

files = glob.glob(destpath+"*")

print "Destination files {}".format(files)
import pdb;pdb.set_trace()
for line in fileinput.input(files, inplace = 1):
    line = line.replace(stext, rtext)
    sys.stdout.write(line)
