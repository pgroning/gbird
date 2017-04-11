#!/bin/env python
# -*- coding: utf-8 -*-

from IPython.core.debugger import Tracer  # Debugging använd Tracer()()
import sys
import numpy as np
import collections

class PinCount(object):
  """ Count pintypes """

  def __init__(self, LFU, FUE, fuetype, verbose=False):
    """ init """
    self.LFU = LFU
    self.FUE = _fixafue(FUE)
    self.fuetype = fuetype
    if verbose: print "PinCount initiated, fuetype = " + fuetype + ", number of segments = " + str(len(self.LFU))
    if not self.__totrod():
      print "False"
      return
    self.__count(fuetype)
    self.noofpintypes = len(self.pintypes)+len(self.pintypes_spec)

  def __count(self,fuetype):
    """ Count all different pintypes """
    pintypes = collections.defaultdict(dict)
    pint = collections.defaultdict(list)
    index = 0
    # special pintypes (bärande, hellång förlängt plenum, etc)
    pintypes_spec = collections.defaultdict(dict)
    pint_spec = collections.defaultdict(dict)
    index_spec = 0
    #
    keys = self.totrod.keys()
    for i in keys[1:]:
      if specialpos(i,fuetype):
        [pintypes_spec,pint_spec,index_spec] = _addpin(self.totrod[i],pintypes_spec,pint_spec,index_spec)
      elif iswaterpos(i,fuetype):
        1
      else:
        [pintypes,pint,index] = _addpin(self.totrod[i],pintypes,pint,index)
    self.pintypes = pintypes
    self.pint = pint
    self.pintypes_spec = pintypes_spec
    self.pint_spec = pint_spec

  def __totrod(self):
    """ Put together segments for all rods"""
    totrod   = collections.defaultdict(list)
    totfuenr = collections.defaultdict(list)
    for i in range(len(self.LFU)):
      [dimx, dimy] = self.LFU[i].shape
      fuearr = {}
      for ii in range(len(self.FUE[i])):
        fueidx = int(self.FUE[i][ii][0])
        fuearr[fueidx] = self.FUE[i][ii][1:]
      for j in range(dimx):
        for k in range(dimy):
          lfuval = int(self.LFU[i][j,k])
          if lfuval in fuearr:
            totrod[j,k].append(fuearr[lfuval])
            totfuenr[j,k].append(lfuval)
          elif lfuval == 0:
            totrod[j,k].append(np.array([0]))
            totfuenr[j,k].append(0)
          else:
            print "Finns inte: " + str(lfuval)
            return False
    self.totrod   = totrod
    self.totfuenr = totfuenr
    return True

def specialpos(pos,fuetype):
  [i,j] = pos
  if fuetype == "OPT3":
    if (pos == (1,3) or pos == (1,7) or pos == (3,1) or pos == (3,9) or 
        pos == (7,1) or pos == (7,9) or pos == (9,3) or pos == (9,7)): 
      return True
  elif fuetype == "AT10XM":
    if ( ((i == 0 or i == 9) and (j != 0 and j != 9)) or
         ((j == 0 or j == 9) and (i != 0 and i != 9)) ):
      return True
  return False

def iswaterpos(pos,fuetype):
  [i,j] = pos
  if fuetype == "OPT2" or fuetype == "OPT3":
    if ( (i == 5) or (j == 5) or ( ((i>=4) and (i<=6)) and ((j>=4) and (j<=6)) ) ):
      return True
  elif fuetype == "AT10XM" or fuetype == "A10B":
    if ((i>=4) and (i<=6)) and ((j>=4) and (j<=6)):
      return True
  return False
    
""" private functions to module pincount """
def _fixafue(FUE):
  """ Byter ut Nan mot 0 i FUE """
  for i in range(len(FUE)):
    for j in range(len(FUE[i])):
      for k in range(len(FUE[i][j])):
        if np.isnan(FUE[i][j][k]): FUE[i][j][k]=0
  return FUE

def _isequal(pin1,pin2):
  """ Check if pin1 == pin2 """
  if len(pin1) != len(pin2): return False
  for i in range(len(pin1)): 
    if not np.array_equal(pin1[i],pin2[i]): return False
  return True

def _addpin(pin1,pintypes1,pint1,index1):
  for i in pintypes1.keys():
    if _isequal(pin1,pintypes1[i]):
      pint1[i] += 1
      return [pintypes1,pint1,index1]
  index1 += 1
  pintypes1[index1] = pin1
  pint1[index1] = 1
  return pintypes1,pint1,index1

if __name__ == '__main__':
  PinCount(sys.argv[1],sys.argv[2],sys.argv[3],verbose=True)
