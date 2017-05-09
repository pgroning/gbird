#!/bin/env python
# -*- coding: utf-8 -*-
# for debugging. Add Tracer()() inside the code at desired line to break at that line
from IPython.core.debugger import Tracer 
import matplotlib.pyplot as plt           # nice with plot-possibilities for debugging
#
import numpy as np
import sys
import os.path
import re

class opt3_defaults(object):
  """ store default-data for opt3 """
  def __init__(self):
    self.def_file = os.path.dirname(__file__) + "/lib/opt3.defaults"
    
  def read_defaults(self,verbose=False):
    if verbose: print "Reading: " + self.def_file
    with open(self.def_file) as inp:
      for line in inp:
        line = re.sub('#.*$','',line)          # strip comments
        if re.search('^\s*$',line): continue   # skip empty row
        line=line.rstrip()
        if re.search('^\s*rv70:',line.lower()):
          self.rv70 = float(line.split(':')[1])
        if re.search('^\s*hfg:',line.lower()):
          self.hfg = float(line.split(':')[1])
        if re.search('^\s*g:',line.lower()):
          self.G = float(line.split(':')[1])
        if re.search('^\s*xin:',line.lower()):
          self.xin = float(line.split(':')[1])
        if re.search('^\s*axial:',line.lower()):
          line = re.sub('^\s*axial:','',line)
          line = re.sub(',',' ',line)
          self.axial = line.split()
    self.fileisread = True

  def get_defaults(self):
    try:
      if self.fileisread:
        return
    except AttributeError:
      self.read_defaults(verbose=False)


def btf_opt3(POW3):
  """
  Subroutine btf_opt3: Calculating BTF for OPT3
  IN:  POW3    - Pin powers for assembly (3-D)
  OUT: RFACTUT - Rfactors for assembly (2-D)
  """
  # initialize
  sub1=np.zeros((POW3.shape[0],5,5))  #  1 | 2  Sub-bundle order 
  sub2=np.zeros((POW3.shape[0],5,5))  #  -----
  sub3=np.zeros((POW3.shape[0],5,5))  #  4 | 3
  sub4=np.zeros((POW3.shape[0],5,5))  #
  MAPI=np.zeros((11,11),dtype=int)    #
  MAPJ=np.zeros((11,11),dtype=int)    #
  #
  i1, j1 =  0,  0
  i2, j2 =  0, 10
  i3, j3 = 10, 10
  i4, j4 = 10,  0
  #
  for i in range(5):
    for j in range(5):
      sub1[:,i,j]=POW3[:,i1,j1]
      sub2[:,i,j]=POW3[:,i2,j2]
      sub3[:,i,j]=POW3[:,i3,j3]
      sub4[:,i,j]=POW3[:,i4,j4]
      MAPI[i1,j1]=i
      MAPI[i2,j2]=i
      MAPI[i3,j3]=i
      MAPI[i4,j4]=i
      MAPJ[i1,j1]=j
      MAPJ[i2,j2]=j
      MAPJ[i3,j3]=j
      MAPJ[i4,j4]=j
      j1=j1+1
      i2=i2+1
      j3=j3-1
      i4=i4-1
    # end j-loop
    i1=i1+1
    j1-=5
    i2-=5
    j3+=5
    i4+=5
    j2=j2-1
    i3=i3-1
    j4=j4+1
  # end i-loop
  # Sub-bundle power mismatch
  SumTot = np.sum(POW3)
  Fsub1 = np.sum(sub1)/SumTot*4
  Fsub2 = np.sum(sub2)/SumTot*4
  Fsub3 = np.sum(sub3)/SumTot*4
  Fsub4 = np.sum(sub4)/SumTot*4
  # subBundle Rfact
  rfac1 = calc_sub(sub1) + mismatchCorr(Fsub1)
  rfac2 = calc_sub(sub2) + mismatchCorr(Fsub2)
  rfac3 = calc_sub(sub3) + mismatchCorr(Fsub3)
  rfac4 = calc_sub(sub4) + mismatchCorr(Fsub4)
  # put together Rfact for full bundle
  RFACTUT = np.zeros((11,11))
  RFACTUT[0:5,0:5] = rfac1[MAPI[0:5,0:5],MAPJ[0:5,0:5]]
  RFACTUT[0:5,6: ] = rfac2[MAPI[0:5,6: ],MAPJ[0:5,6: ]]
  RFACTUT[6: ,6: ] = rfac3[MAPI[6: ,6: ],MAPJ[6: ,6: ]]
  RFACTUT[6: ,0:5] = rfac4[MAPI[6: ,0:5],MAPJ[6: ,0:5]]
  RFACTUT[4,4]=0.0
  RFACTUT[6,6]=0.0
  RFACTUT[4,6]=0.0
  RFACTUT[6,4]=0.0
  #
  return RFACTUT

def mismatchCorr(fsub):
  """
  Subroutine mismatchCorr - Calculates subbundle mismatch rfactor ΔR ( R -> R + ΔR )
  IN:  Fsub = sub-bundle power mismatch
  OUT: ΔR   = −1.1325 + 1.4900 * FSUB − 0.3575 * FSUB^2 (Report BTA 09-1033, rev 0, page 4, Chap 2, EQ 3)
  """
  deltaR = -1.1325 + 1.4900 * fsub - 0.3575 * fsub**2
  return deltaR

def calc_sub(sub_bundle):
  """
  Subroutine calc_sub: calculates rfactors for a sub-bundle
  IN:  sub_bundle - pin power for sub-bundle (3-D)
  OUT: Rglob      - rfactors for sub-bundle  (2-D)
  """
  sub_norm = norm_sub(sub_bundle)
  epsilon  = 0.0001
  # get defaults
  try:
    defaults
  except:
    defaults = opt3_defaults()
  defaults.get_defaults()
  #
  ax_def = np.array(map(float,defaults.axial))  # typiska värden:
  rv70   = defaults.rv70                        # rv70 =  1    # relative gas density
  hfg    = defaults.hfg                         # hfg  =  1.5  # latent heat [MJ/kg
  G      = defaults.G                           # G    =  1.5  # Mass flow [10^3 kg/m2/s]
  xin    = defaults.xin                         # xin  = -0.03 # typical subcooling
  # ax power profile
  noder = sub_bundle.shape[0]
  APLHGR = get_ax_eff(noder,ax_def)
  APLHGR=APLHGR/np.sum(APLHGR)*noder
  #
  LHGR  = np.array(sub_norm)
  I1rod = np.array(sub_norm)
  I2rod = np.array(sub_norm)
  xc    = np.array(sub_norm)
  cpr   = np.array(sub_norm)
  Rglob = np.zeros((5,5))
  for k in range(noder):
    LHGR[k,:,:] = sub_norm[k,:,:]*APLHGR[k]
  #
  xout  = 0.5     # critical quality guess
  Lheat = 3.68    # heated length
  #
  iloop = 0
  while (True):
    iloop += 1
    Q     = np.cumsum(APLHGR)*Lheat/noder
    Qnorm = Q/Q[-1]    
    x     = xin+(xout-xin)*Qnorm
    # I1 integrates only the boiling part
    I1=np.cumsum(APLHGR*(x>0))*Lheat/noder
    I2=np.cumsum(I1*(x>0))*Lheat/noder/(Lheat*I1)
    I2[x<0]=0.0
    for i in range(5):
      for j in range(5):
        if i==4 and j==4:
          break
        I1rod[:,i,j]=np.cumsum(LHGR[:,i,j]*(x>0))*Lheat/noder
        I2rod[:,i,j]=np.cumsum(I1rod[:,i,j]*(x>0))*Lheat/noder/(Lheat*I1rod[:,i,j])
    I1rod[LHGR<epsilon] = 0.0
    I2rod[LHGR<epsilon] = 0.0
    #
    R=RfacD5(I1,I2,I1rod,I2rod) # these are local rod R-factors
    R[x<0,:,:]=0.0
    #
    mincpr=100
    for i in range(5):
      for j in range(5):
        if (i==4 and j==4):
          break
        xc[:,i,j] = xcD5(R[:,i,j],I2,G,rv70,hfg)
        cpr[:,i,j]=(xc[:,i,j]-xin)/(x-xin)  # pseudo-cpr on rod level
        mincpr = min(mincpr,np.min(cpr[:,i,j]))        
        # Calculate equivalent global R-factor, this is what we
        # shall report back. Is used only to guide nuclear design.
        Rglob[i,j]=invxcD5(xin+(xout-xin)*np.min(cpr[:,i,j]),I2[-1],G,rv70,hfg)
    #
    if abs(mincpr-1)<0.05:
      break
    xout=xin+(xout-xin)*mincpr
    if iloop > 100:
      # TODO: ett felmeddelande här!!!
      break  # no convergence
  #Tracer()()
  return Rglob

def get_ax_eff(noder,ax_def):
  """
  Subroutine get_ax_eff:
  """
  ax_def = np.append(ax_def,0.0)   # append 0.0
  ax_def = np.insert(ax_def,0,0.0) # prepend 0.0
  ax_ut    = np.zeros(noder)
  xp       = np.zeros(25+2)
  xp[-1]   = 1.0
  xp[1:-1] = np.linspace(1./25,1,25)-1./50
  #
  x = np.linspace(1./noder,1,noder)-1./(2*noder)
  ax_ut = np.interp(x,xp,ax_def)
  #
  return ax_ut

def RfacD5(I1,I2,I1rod,I2rod):
  """
  Subroutine RfacD5:
  """
  e=np.array([[ 0.300,  -0.008, -0.018,   0.042,  0.045 ],
              [-0.0086,  0.0332,-0.0119,  0.0269, 0.0304],
              [-0.0189, -0.0119, 0.0094,  0.0521, 0.0412],
              [ 0.0426,  0.0269, 0.0521, -0.0259, 0.1514],
              [ 0.0456,  0.0304, 0.0412,  0.1514, 0.00  ]])
  a=0.3
  b=0.4406
  c=0.0926
  d=0.0553
  Rfac = np.zeros(I1rod.shape)
  epsilon = 0.0001
  for i in range(5):
    for j in range(5):
      if (i==4 and j==4):
        break
      for k in range(I1rod.shape[0]):
        if I1rod[k,i,j]<epsilon:
          continue
        Ns=0
        Nd=0
        R=I1rod[k,i,j]**b
        if i>0 and I1rod[k,i-1,j]>epsilon:
          Ns=Ns+1
          R=R+c*I1rod[k,i-1,j]**b
        if (i<4 and j!=4) and I1rod[k,i+1,j]>epsilon:
          Ns=Ns+1
          R=R+c*I1rod[k,i+1,j]**b
        if (j>0) and I1rod[k,i,j-1]>epsilon:
          Ns=Ns+1
          R=R+c*I1rod[k,i,j-1]**b
        if (j<4 and i!=4) and I1rod[k,i,j+1]>epsilon:
          Ns=Ns+1
          R=R+c*I1rod[k,i,j+1]**b
        if (i>0 and j>0) and I1rod[k,i-1,j-1]>epsilon:
          Nd=Nd+1
          R=R+d*I1rod[k,i-1,j-1]**b
        if (i>0 and j<4) and I1rod[k,i-1,j+1]>epsilon:
          Nd=Nd+1
          R=R+d*I1rod[k,i-1,j+1]**b
        if (i<4 and j>0) and I1rod[k,i+1,j-1]>epsilon:
          Nd=Nd+1
          R=R+d*I1rod[k,i+1,j-1]**b
        if (i<4 and j<4 and not (i==3 and j==3)) and I1rod[k,i+1,j+1]>epsilon:
          Nd=Nd+1
          R=R+d*I1rod[k,i+1,j+1]**b
        Rfac[k,i,j]=R/((1+c*Ns+d*Nd)*I1[k]**b)*(I2[k]/I2rod[k,i,j])**a*(1+e[i,j])
  return Rfac

def invxcD5(xc,I2,G,rv70,hfg):
  """
  Subroutine invxcD5: calculates R-factors
  IN:  xc   - critical quality
  IN:  I2   - I2-parameter
  IN:  G    - mass flow [10^3 kg/m2/s]
  IN:  rv70 - relative gas density
  IN:  hfg  - latent heat [MJ/kg]
  OUT: R    - R-factors
  """
  a=np.array((-2.0477, 1.6064, -2.9805, 1.5110, 0.2880, 2.9443, -0.3807, -1.8105, 0.5158, 1.0976, 0.8062))
  I2m=np.min(a[8]*(I2/a[8])**((min(G/a[9],1))**a[10]),0.572)
  R=np.log(xc/(np.exp(1.0/(1+np.exp(a[0]+a[1]*G))+a[2]/(I2m+1)+a[3])*(rv70+a[4])*hfg**a[5]+a[6]*rv70))/a[7]
  return R

def xcD5(R,I2,G,rv70,hfg):
  """
  Subroutine xcD5: calculates critical quality
  IN:  R    - R-factors (vector)
  IN:  I2   - I2-paramter (vector)
  IN:  G    - mass fllow [10^3 kg/m2/s]
  IN:  rv70 - relative gas density
  IN:  hfg  - latent heat [MJ/kg]
  OUT: xc   - critical quality
  """
  a=np.array((-2.0477, 1.6064, -2.9805, 1.5110, 0.2880, 2.9443, -0.3807, -1.8105, 0.5158, 1.0976, 0.8062))
  I2m=np.minimum(a[8]*(I2[-1]/a[8])**((min(G/a[9],1))**a[10]),0.572)
  xc=(np.exp(1.0/(1+np.exp(a[0]+a[1]*G))+a[2]/(I2m+1)+a[3])*(rv70+a[4])*hfg**a[5]+a[6]*rv70)*np.exp(a[7]*R)
  return xc
  
def norm_sub(sub_bundle):
  """ 
  Subroutine norm_sub: normalizes subbundle
  IN:  sub_bundle      - sub-bundle
  OUT: sub_bundle_norm - normalized sub-bundle
  """
  sub_bundle_norm = np.array(sub_bundle)
  epsilon = 0.0001
  for i in range(sub_bundle.shape[0]):
    sum_nodplan  = np.sum(sub_bundle[i,:,:])                               # sum av nodplan 
    num_fuelrods = np.sum(sub_bundle[i,:,:]>epsilon)                        # antal bränslestavar i nodplanet
    sub_bundle_norm[i,:,:] = sub_bundle[i,:,:]/sum_nodplan*num_fuelrods    # normerat bränsleplan
  return sub_bundle_norm

if __name__ == '__main__':
  POW3 = sys.argv[1]
  btf_opt3(POW)
  
