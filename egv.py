#!/bin/env python
# -*- coding: utf-8 -*-
from IPython.core.debugger import Tracer  # Debugging använd Tracer()()
import sys
import os
import re
from subprocess import call, Popen, STDOUT, PIPE
import shlex  # used for splitting subprocess call argument string into a list

def run_egv(inpfil, egv_version,verbose=False):
  """Run egv"""
  if verbose: 
    print "run_egv:"
    print "  {0:<20} {1:<}".format("egv-inputfil:",inpfil)
    print "  {0:<20} {1:<}".format("egv-version:",egv_version)
  egvexe = "egv -v " + egv_version
  arglist = shlex.split(egvexe + " " + inpfil)
  #call(arglist)
  a = Popen(arglist,stdout=PIPE)
  a.wait()

def check_egv_run(listfil,verbose=False):
  """Check if egv-run OK"""
  if verbose: 
    print "check_egv_run:"
    print "  {0:<20} {1:<}".format("kontrollerar fil:",listfil)
  if not os.path.isfile(listfil):
    print "ERROR: no listfile ({0}), egv-run not ok".format(listfil)
    return False
  with open(listfil) as f:
    flines = f.read().splitlines()
  pattern = '^\s*Nej'
  flag = True
  for line in flines:
    match = re.search(pattern, line)
    if match:
      flag = False
      if verbose: print line
  return flag

def create_egv_inp(reactor,fuel,name,cax,filename="egv-indata.txt",verbose=False):
  """Create egv-input"""
  if verbose: 
    print "create_egv_inp:"
    print "  Skapar indatafil till egv: {0:<}".format(filename)
  try:
    f = open(filename,'w')
  except:
    print "ERROR: can't open/create file {0:<}".format(filename)
    return False
  # skapar input-fil till egv
  f.write("{0:<25} {1:<}{2:<}\n".format("TITEL","Greenbird run for ",fuel))
  f.write("{0:<25} {1:<}\n".format("REAKTOR",reactor))
  f.write("{0:<25} {1:<}\n".format("PATRONSORT",fuel))
  for i in range(len(cax)):
    fil = cax[i]["FIL"]
    if not os.path.isfile(fil):
      print "Couldn't find file " + fil
      return False
    fil = os.path.abspath(fil)
    f.write("CAX {0:<1} {1:<19} {2:<}\n".format(i+1,cax[i]["ZON"],fil))    
  f.write("{0:<25} {1:<}\n".format("ALLMAENNAKRAVUTFIL",name+"-allmaennakrav-egv.txt"))
  f.write("{0:<25} {1:<}\n".format("PLRKRAVUTFIL",name+"-plrkrav-egv.txt"))
  f.write("{0:<25} {1:<}\n".format("BAKRAVUTFIL",name+"-bakrav-egv.txt"))
  f.write("{0:<25} {1:<}\n".format("A1A2KRAVUTFIL",name+"-a1a2krav-egv.txt"))
  f.write("{0:<25} {1:<}\n".format("KRITICITETSKRAVUTFIL",name+"-kriticitetskrav-egv.txt"))
  listfil = name + "-lista-egv.txt"
  f.write("{0:<25} {1:<}\n".format("LISTUTFIL",listfil))
  f.close()
  return [filename,listfil]

def do_egv(reactor, fuel, caxfiles, runname=None, egvinpfile="egv-indata.txt", egv_version="2.3.0", verbose=False ):
  """Create input and run egv. Check if run ok"""

  if runname is None:
    runname = "gb-"+fuel   # default namn

  # skapa egv-input
  egvfiler = create_egv_inp(reactor,fuel,runname,caxfiles,verbose=verbose,filename=egvinpfile)
  if egvfiler == False:
    return False

  # tar bort egv-list-fil om den finns
  listfil = egvfiler[1]
  if os.path.isfile(listfil):
    os.remove(listfil)

  # kör egv
  egvinput = egvfiler[0]
  run_egv(egvinput,egv_version,verbose=verbose)

  # kontrollera körning
  flag = check_egv_run(listfil,verbose=verbose)

  if flag:
    if verbose: print "Run OK"
  else:
    print "ERROR: EGV-Run NOT OK"

  return flag

if __name__=='__main__':
  reactor     = sys.argv[1]
  fuel        = sys.argv[2]
  egv_version = sys.argv[3]
  verbose = False
  if len(sys.argv)>4 and sys.argv[4] == "True":
      verbose = True

  fil1 = {"ZON" : "NEDRE AKTIVZON", "FIL" : "../TEST/EGV/2.3.0-T3/cax/e34ATXM/e34ATXM-396-10g50dom-cas.cax"}
  fil2 = {"ZON" : "ÖVRE  AKTIVZON", "FIL" : "../TEST/EGV/2.3.0-T3/cax/e34ATXM/e34ATXM-394-10g50ple-cas.cax"}
  fil3 = {"ZON" : "ÖVRE  AKTIVZON", "FIL" : "../TEST/EGV/2.3.0-T3/cax/e34ATXM/e34ATXM-394-10g50van-cas.cax"}
  caxfiles = [fil1, fil2, fil3]
  do_egv(reactor,fuel,caxfiles,egv_version=egv_version,verbose=verbose)
