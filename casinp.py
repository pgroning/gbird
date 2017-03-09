#!/bin/env python
# -*- coding: utf-8 -*-
"""
Module for updating TIT, FUE and LFU cards in Casmo input.
- input for constructor: list of class segment with attributes caxfiles, LFU, FUE, TIT
- methods:
-          existfiles : checks if casmo-input exists
-          createinp  : create new casmo-input starting with old input and updates LFU,FUE,TIT cards
"""
from IPython.core.debugger import Tracer  # Debugging använd Tracer()()
import os
import sys
import re
import numpy as np

class Casinp(object):
  """ create casmo input with updated TIT, FUE and LFU cards"""

  def __init__(self, seglist,verbose=False):
    """ init """
    self.caxfiles = []
    self.LFU      = []
    self.FUE      = []
    self.TIT      = []
    #
    for i in range(len(seglist)):
      self.caxfiles.append(seglist[i].data.caxfile)
      self.LFU.append(seglist[i].data.LFU)
      self.FUE.append(seglist[i].data.FUE)
      self.TIT.append(seglist[i].data.TIT)

  def existfiles(self,verbose=False):
    """
    Check if Casmo inputfile(s) exists
    """
    flag = 0
    if not hasattr(self,'caxfiles'):
      print "ERROR: no attribute caxfiles"
      flag = 1000
      return flag
    elif self.caxfiles == []:
      print "ERROR: caxfiles empty, no files to check"
      flag = 1000
      return flag
    else:
      caxfiles = self.caxfiles
    # initialisation
    inputfiles  = []
    newinpfiles = []
    backupfiles = []
    errmess     = []
    warnmess    = []
    for i in range(len(caxfiles)):                  # loop over caxfiles
      basename = os.path.splitext(caxfiles[i])[0]   # remove suffix .cax
      inputfiles.append(basename +'.inp')           # basename.inp
      newinpfiles.append(basename + ".T.inp")       # basename.T.inp
      backupfiles.append(basename + ".TT.inp")      # basename.TT.inp
      if not os.path.isfile(inputfiles[i]):
        tmpstr = "ERROR: casmo-input {0} does not exist".format(inputfiles[i])
        if verbose: print tmpstr
        errmess.append(tmpstr)
        flag += 100
      if os.path.isfile(newinpfiles[i]):
        tmpstr = "WARNING: casmo-input {0} does exist".format(newinpfiles[i])
        if verbose: print tmpstr
        warnmess.append(tmpstr)
        flag += 1
    # sätter data
    self.caxfiles    = caxfiles
    self.inputfiles  = inputfiles
    self.newinpfiles = newinpfiles
    self.backupfiles = backupfiles
    self.errmess     = errmess
    self.warnmess    = warnmess
    return flag

  def createinp(self, backup=False,verbose=False):
    """
    Create casmo input
    """
    for i in range(len(self.inputfiles)):
      if verbose: print "Fil: {0}".format(self.inputfiles[i])
      # backup
      if backup:
        if os.path.isfile(self.newinpfiles[i]):
          try:
            os.rename(self.newinpfiles[i], self.backupfiles[i])
          except:
            print "ERROR: can't move file {0:<} to {1}".format(self.newinpfiles[i], self.backupfiles[i])
            return False
      # open casmo-inp
      with open(self.inputfiles[i]) as cinp:
        cinpl = cinp.read().splitlines()
      cinp.close()
      # open test-input
      try:
        f = open(self.newinpfiles[i],'w')
      except:
        print "ERROR: can't create file {0:<}".format(self.newinpfiles[i])
        return False
      # loop through file
      titpat = '^TIT\s*'
      fuepat = '^FUE\s*'
      lfupat = '^LFU\s*'
      flagfue = False
      lidx = 0
      while lidx<len(cinpl):
        line   = cinpl[lidx]
        lidx  += 1
        matcht = re.search(titpat,line)  # search for TIT
        matchf = re.search(fuepat,line)  # search for FUE
        matchl = re.search(lfupat,line)  # search for LFU
        if matcht:
          f.write("TIT * {0:<}\n".format(self.TIT[i]))
        elif matchf:
          if not flagfue:
            fue = self.FUE[i]
            for fl in range(len(fue)):
              if np.isnan(fue[fl,3]) or np.isnan(fue[fl,4]):
                fuestr = "FUE {0:>2.0f} {1:>6.3f}/{2:<.3f}\n".format(fue[fl,0],fue[fl,1],fue[fl,2])
              else:
                fuestr = "FUE {0:>2.0f} {1:>6.3f}/{2:<.3f} {3:>.0f}={4:<.3f}\n".format(fue[fl,0],fue[fl,1],fue[fl,2],fue[fl,3],fue[fl,4])
              f.write(fuestr)
            flagfue = True
        elif matchl:
          f.write("LFU\n")
          lfu = self.LFU[i]
          for ll in range(len(lfu)):
            for mm in range(ll+1):
              f.write("{0:>2.0f} ".format(lfu[ll,mm]))
            f.write("\n")
          lidx += len(lfu) 
        else:
          f.write("{0}\n".format(line))
      f.close()
    return True

if __name__ == '__main__':
  pass


