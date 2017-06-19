#!/bin/env python
# -*- coding: utf-8 -*-
# for debugging. Add Tracer()() inside the code at desired line to break at that line
#from IPython.core.debugger import Tracer 
#import matplotlib.pyplot as plt           # nice with plot-possibilities for debugging
#
import numpy as np
import sys
import os.path
import re

class opt3_defaults(object):
  """ store default-data for opt3 """
  def __init__(self,verbose = False):
    self.def_file = os.path.dirname(__file__) + "/opt3.defaults"
    self.read_defaults(verbose = verbose)
    
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

def btf_opt3(POW3in):
  """
  Subroutine btf_opt3: Calculating BTF for OPT3
  IN:  POW3    - Pin powers for assembly (3-D)
  OUT: RFACTUT - Rfactors for assembly (2-D)
  """
  defaults = opt3_defaults()
  POW3 , num_fuelrods = norm_sub(POW3in,96)
  nodes = POW3.shape[0]
  ax_def = np.array(map(float,defaults.axial))  # typiska värden:
  APLHGR = get_ax_eff(nodes,ax_def)
  APLHGR=APLHGR/np.sum(APLHGR)*nodes
  LHGR  = np.zeros(POW3.shape)
  for k in range(nodes):
    LHGR[k,:,:] = POW3[k,:,:]*APLHGR[k]
  #
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
      sub1[:,i,j]=LHGR[:,i1,j1]
      sub2[:,i,j]=LHGR[:,i2,j2]
      sub3[:,i,j]=LHGR[:,i3,j3]
      sub4[:,i,j]=LHGR[:,i4,j4]
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
  SumTot = np.sum(LHGR)
  Fsub1 = np.sum(sub1)/SumTot*4
  Fsub2 = np.sum(sub2)/SumTot*4
  Fsub3 = np.sum(sub3)/SumTot*4
  Fsub4 = np.sum(sub4)/SumTot*4
  # subBundle Rfact
  q_fuelrods = num_fuelrods/4
  rfac1 = calc_sub(sub1, defaults, q_fuelrods) + mismatchCorr(Fsub1)
  rfac2 = calc_sub(sub2, defaults, q_fuelrods) + mismatchCorr(Fsub2)
  rfac3 = calc_sub(sub3, defaults, q_fuelrods) + mismatchCorr(Fsub3)
  rfac4 = calc_sub(sub4, defaults, q_fuelrods) + mismatchCorr(Fsub4)
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

def calc_sub(LHGRsub, defaults, fuelrods):
  """
  Subroutine calc_sub: calculates rfactors for a sub-bundle
  IN:  sub_bundle - pin power for sub-bundle (3-D)
  IN:  defaults   - default-values from file opt3.defaults
  OUT: Rglob      - rfactors for sub-bundle  (2-D)
  """
  epsilon  = 0.0001
  #
  ax_def = np.array(map(float,defaults.axial))  # typiska värden:
  rv70   = defaults.rv70                        # rv70 =  1    # relative gas density
  hfg    = defaults.hfg                         # hfg  =  1.5  # latent heat [MJ/kg
  G      = defaults.G                           # G    =  1.5  # Mass flow [10^3 kg/m2/s]
  xin    = defaults.xin                         # xin  = -0.01 # typical subcooling
  #
  nodes = LHGRsub.shape[0]
  I1rod = np.zeros(LHGRsub.shape)
  I2rod = np.zeros(LHGRsub.shape)
  xc    = np.zeros(LHGRsub.shape)
  cpr   = np.zeros(LHGRsub.shape)
  Rglob = np.zeros((5,5))
  #
  xout  = 0.5     # critical quality guess
  Lheat = 3.68    # heated length
  #
  iloop = 0
  APF = np.zeros(LHGRsub.shape[0])
  while (True):
    iloop += 1
    for i in range(nodes):
      APF[i] = np.sum(LHGRsub[i,:,:])/fuelrods[i]
    Q     = np.cumsum(APF)*Lheat/nodes
    Qnorm = Q/Q[-1]    
    x     = xin+(xout-xin)*Qnorm
    # I1 integrates only the boiling part
    I1=np.cumsum(APF*(x>0))*Lheat/nodes
    I2=np.cumsum(I1*(x>0))*Lheat/nodes/(Lheat*I1)
    I2[x<0]=0.0
    for i in range(5):
      for j in range(5):
        if i==4 and j==4:
          break
        I1rod[:,i,j]=np.cumsum(LHGRsub[:,i,j]*(x>0))*Lheat/nodes
        I2rod[:,i,j]=np.cumsum(I1rod[:,i,j]*(x>0))*Lheat/nodes/(Lheat*I1rod[:,i,j])
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
    #
    if iloop > 5:
      print "WARNING: no convergence in btf_opt3:calc_sub"  # TODO: returnera nåt felmeddelande??
      break  # no convergence
  #Tracer()()
    
  return Rglob

def get_ax_eff(nodes,ax_def):
  """
  Subroutine get_ax_eff:
  IN:  nodes  - desired number of nodes in axial power profile 
  IN:  ax_def - axial power profile
  OUT: ax_ut  - the new interpolated axial power profile
  """
  ax_def = np.append(ax_def,0.0)   # append 0.0
  ax_def = np.insert(ax_def,0,0.0) # prepend 0.0
  ax_ut    = np.zeros(nodes)
  xp       = np.zeros(25+2)
  xp[-1]   = 1.0
  xp[1:-1] = np.linspace(1./25,1,25)-1./50
  #
  x = np.linspace(1./nodes,1,nodes)-1./(2*nodes)
  ax_ut = np.interp(x,xp,ax_def)
  #
  return ax_ut

def RfacD5(I1,I2,I1rod,I2rod):
  """
  Subroutine RfacD5:
  IN:  I1
  IN:  I2
  IN:  I1rod
  IN:  I2rod
  OUT: Rfact - rfactors for subbundle
  """
  e=np.array([[ 0.300,  -0.0086,-0.0189,  0.0426, 0.0456],
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
  Rb  = I1rod[:,:,:]**b
  dRb = d*Rb
  cRb = c*Rb
  I1b = I1**b
  nodes = I1rod.shape[0]
  krange = xrange(nodes)
  #I1bool = I1rod>epsilon
  I1bool = np.ones(I1rod.shape,dtype=bool)
  for i in xrange(5):
    for j in xrange(5):
      if (i==4 and j==4):
        break # water      
      for k in krange:
        if I1rod[k,i,j]<epsilon:
          continue
        if (i==0 and j==0 and k>int(10./25*nodes)): continue                      # SLR in NW
        if ((i==4 and j==3) or (i==3 and j==4)) and k>int(18./25*nodes): continue # PLR
        Ns=0
        Nd=0
        R=Rb[k,i,j]
        if i>0 and I1bool[k,i-1,j]:
          Ns=Ns+1
          R=R+cRb[k,i-1,j]
        if i<4 and I1bool[k,i+1,j]:
          if not (i==3 and j==4):
            Ns=Ns+1
            R=R+cRb[k,i+1,j]
        if (j>0) and I1bool[k,i,j-1]:
          Ns=Ns+1
          R=R+cRb[k,i,j-1]
        if j<4 and I1bool[k,i,j+1]:
          if not (i==4 and j==3):
            Ns=Ns+1
            R=R+cRb[k,i,j+1]
        if (i>0 and j>0) and I1bool[k,i-1,j-1]:
          Nd=Nd+1
          R=R+dRb[k,i-1,j-1]
        if (i>0 and j<4) and I1bool[k,i-1,j+1]:
          Nd=Nd+1
          R=R+dRb[k,i-1,j+1]
        if (i<4 and j>0) and I1bool[k,i+1,j-1]:
          Nd=Nd+1
          R=R+dRb[k,i+1,j-1]
        if (i<4 and j<4 and not (i==3 and j==3)) and I1bool[k,i+1,j+1]:
          Nd=Nd+1
          R=R+dRb[k,i+1,j+1]
        Q1 = (I2[k]/I2rod[k,i,j])**a
        Rfac[k,i,j]=R/((1+c*Ns+d*Nd)*I1b[k])*(1+e[i,j])*min(1.1,max(Q1,0.9))
        #Rfac[k,i,j]=R/((1+c*Ns+d*Nd)*I1b[k])*(I2[k]/I2rod[k,i,j])**a*(1+e[i,j])
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
  
def norm_sub(sub_bundle, fuelrods):
  """ 
  Subroutine norm_sub: normalizes subbundle
  IN:  sub_bundle      - sub-bundle
  IN:  fuelrods        - number of fuelrods
  OUT: sub_bundle_norm - normalized sub-bundle
  OUT: num_fuelrods    - fuelrods in each node-plane
  """
  sub_bundle_norm = np.zeros(sub_bundle.shape)
  nodes = sub_bundle.shape[0]
  num_fuelrods = np.zeros(nodes)
  epsilon = 0.0001
  for i in range(nodes):
    sum_nodplan  = np.sum(sub_bundle[i,:,:])                                  # sum av nodplan 
    num_fuelrods[i] = np.sum(sub_bundle[i,:,:]>epsilon)                       # antal bränslestavar i nodplanet
    sub_bundle_norm[i,:,:] = sub_bundle[i,:,:]/sum_nodplan*fuelrods           # normerat bränsleplan
  return sub_bundle_norm, num_fuelrods

if __name__ == '__main__':
  POW3 = sys.argv[1]
  btf_opt3(POW)
  
