#!/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import sys
import math

def btf_opt3(POW3):
  """Calculating BTF for OPT3"""
  sub1=np.zeros((POW3.shape[0],5,5))
  sub2=np.zeros((POW3.shape[0],5,5))
  sub3=np.zeros((POW3.shape[0],5,5))
  sub4=np.zeros((POW3.shape[0],5,5))
  MAPI=np.zeros((11,11),dtype=int)
  MAPJ=np.zeros((11,11),dtype=int)
  i1=0
  j1=0

  i2=0
  j2=10

  i3=10
  j3=10

  i4=10
  j4=0
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
  SumTot = np.sum(POW3)
  Fsub1 = np.sum(sub1)/SumTot*4
  Fsub2 = np.sum(sub2)/SumTot*4
  Fsub3 = np.sum(sub3)/SumTot*4
  Fsub4 = np.sum(sub4)/SumTot*4
  # R
  #ΔR = −1.1325 + 1.4900 ⋅ FSUB − 0.3575⋅ FSUB2
  
  #print "POW3:\n" + str(POW3)
  #print "sub1:\n" + str(sub1)
  #print "sub2:\n" + str(sub2)
  #print "sub3:\n" + str(sub3)
  #print "sub4:\n" + str(sub4)
  #print str(Fsub1) + " " + str(Fsub2)
  #print str(Fsub4) + " " + str(Fsub3)
  #print str(SumTot)
  #return
  #sub2 =

  #print "första:"
  #print sub1
  rfac1 = calc_sub(sub1) + mismatchCorr(Fsub1)
  rfac2 = calc_sub(sub2) + mismatchCorr(Fsub2)
  rfac3 = calc_sub(sub3) + mismatchCorr(Fsub3)
  rfac4 = calc_sub(sub4) + mismatchCorr(Fsub4)
  #print "rfac1:\n" + str(rfac1)
  #print "rfac2:\n" + str(rfac2)
  #print "rfac3:\n" + str(rfac3)
  #print "rfac4:\n" + str(rfac4)
  RFACTUT = np.zeros((11,11))
  RFACTUT[0:5,0:5] = rfac1[MAPI[0:5,0:5],MAPJ[0:5,0:5]]
  RFACTUT[0:5,6: ] = rfac2[MAPI[0:5,6: ],MAPJ[0:5,6: ]]
  RFACTUT[6: ,6: ] = rfac3[MAPI[6: ,6: ],MAPJ[6: ,6: ]]
  RFACTUT[6: ,0:5] = rfac4[MAPI[6: ,0:5],MAPJ[6: ,0:5]]
  RFACTUT[4,4]=0.0
  RFACTUT[6,6]=0.0
  RFACTUT[4,6]=0.0
  RFACTUT[6,4]=0.0
  #print "RFACTUT:\n" + str(RFACTUT)
  #np.set_printoptions(precision=2)
  #print "RFACTUT:\n" + str(RFACTUT)
  #print "andra:"
  #print sub1
  return RFACTUT

def mismatchCorr(fsub):
  deltaR = -1.1325+1.4900*fsub-0.3575*fsub**2
  return deltaR

def calc_sub(sub_bundle):
  sub_norm = norm_sub(sub_bundle)
  # ax effekt profil
  noder = sub_bundle.shape[0]
  APLHGR=np.sin(np.linspace(0,np.pi,noder)+0.5)+0.5
  APLHGR=APLHGR/np.sum(APLHGR)*noder;  # temporary
  #print "APLHGR: " + str(APLHGR)
  LHGR = np.array(sub_norm)
  I1rod = np.array(sub_norm)
  I2rod = np.array(sub_norm)
  xc    = np.array(sub_norm)
  cpr   = np.array(sub_norm)
  Rglob = np.zeros((5,5))
  for k in range(noder):
    LHGR[k,:,:] = sub_norm[k,:,:]*APLHGR[k]
  # typiska 
  rv70=1  
  hfg=1.5
  G=1.5     # 1500 kg/m2/s, typical
  xin=-0.03 # typical subcooling
  #
  xout=0.5  # critical quality guess
  Lheat = 3.68

  while (True):        
    Q=np.cumsum(APLHGR)*Lheat/noder
    Qnorm=Q/Q[-1]    
    x=xin+(xout-xin)*Qnorm
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
    I1rod[LHGR<0.0001] = 0.0
    I2rod[LHGR<0.0001] = 0.0
    #print "I1rod"
    #print I1rod
    #print "I2rod"
    #print I2rod
    #break
    # slut loop
    R=RfacD5(I1,I2,I1rod,I2rod) # these are local rod R-factors

    R[x<0,:,:]=0.0
    
    #print "R: " + str(R)

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
    #print "cpr: " + str(cpr)
    #print "xc: " + str(xc)
    #print "x: " + str(x)
    #print "mincpr: " + str(mincpr)
    #print "Rfact:  " + str(Rglob)
    #break
    if abs(mincpr-1)<0.05:
      break
    xout=xin+(xout-xin)*mincpr
  return Rglob

def RfacD5(I1,I2,I1rod,I2rod):
  e=np.array([[ 0.300,  -0.008, -0.018, 0.042, 0.045],
              [-0.0086,  0.0332,-0.0119, 0.0269, 0.0304],
              [-0.0189, -0.0119, 0.0094, 0.0521, 0.0412],
              [ 0.0426,  0.0269, 0.0521, -0.0259, 0.1514],
              [ 0.0456,  0.0304, 0.0412,  0.1514, 0.00]])
  
  a=0.3
  b=0.4406
  c=0.0926
  d=0.0553
  Rfac = np.zeros(I1rod.shape)
  for i in range(5):
    for j in range(5):
      if (i==4 and j==4):
        break
      for k in range(I1rod.shape[0]):
        if I1rod[k,i,j]<0.0001:
          continue
        Ns=0
        Nd=0
        R=I1rod[k,i,j]**b
        if i>0 and I1rod[k,i-1,j]>0.0001:
          Ns=Ns+1
          R=R+c*I1rod[k,i-1,j]**b
        if (i<4 and j!=4) and I1rod[k,i+1,j]>0.0001:
          Ns=Ns+1
          R=R+c*I1rod[k,i+1,j]**b
        if (j>0) and I1rod[k,i,j-1]>0.0001:
          Ns=Ns+1
          R=R+c*I1rod[k,i,j-1]**b
        if (j<4 and i!=4) and I1rod[k,i,j+1]>0.0001:
          Ns=Ns+1
          R=R+c*I1rod[k,i,j+1]**b
        if (i>0 and j>0) and I1rod[k,i-1,j-1]>0.0001:
          Nd=Nd+1
          R=R+d*I1rod[k,i-1,j-1]**b
        if (i>0 and j<4) and I1rod[k,i-1,j+1]>0.0001:
          Nd=Nd+1
          R=R+d*I1rod[k,i-1,j+1]**b
        if (i<4 and j>0) and I1rod[k,i+1,j-1]>0.0001:
          Nd=Nd+1
          R=R+d*I1rod[k,i+1,j-1]**b
        if (i<4 and j<4 and not (i==3 and j==3)) and I1rod[k,i+1,j+1]>0.0001:
          Nd=Nd+1
          R=R+d*I1rod[k,i+1,j+1]**b
        #Rfac[k,i,j]=R/((1+c*Ns+d*Nd)*I1**b)*(I2/I2rod[k,i,j])**a*(1+e[i,j])
        Rfac[k,i,j]=R/((1+c*Ns+d*Nd)*I1[k]**b)*(I2[k]/I2rod[k,i,j])**a*(1+e[i,j])
        #print "Rfac,i,j,k" + str(Rfac[k,i,j]) + str(i) + str(j) + str(k)
  return Rfac

def invxcD5(xc,I2,G,rv70,hfg):
  """ R    - R-factors (vector)
  % I2   - I2-paramter (vector)
  % G    - mass fllow [10^3 kg/m2/s]
  % rv70 - relative gas density
  % hfg  - latent heat [MJ/kg]
  """
  a=np.array((-2.0477, 1.6064, -2.9805, 1.5110, 0.2880, 2.9443, -0.3807, -1.8105, 0.5158, 1.0976, 0.8062))
  I2m=np.min(a[8]*(I2/a[8])**((min(G/a[9],1))**a[10]),0.572)
  R=np.log(xc/(np.exp(1.0/(1+np.exp(a[0]+a[1]*G))+a[2]/(I2m+1)+a[3])*(rv70+a[4])*hfg**a[5]+a[6]*rv70))/a[7]
  return R

def xcD5(R,I2,G,rv70,hfg):
  """ R    - R-factors (vector)
  % I2   - I2-paramter (vector)
  % G    - mass fllow [10^3 kg/m2/s]
  % rv70 - relative gas density
  % hfg  - latent heat [MJ/kg]
  """
  #print "R: " + str(R)
  #print "I2: " + str(I2)
  #print "G,rv70,hfg: " + str(G) + str(rv70) + str(hfg)
  a=np.array((-2.0477, 1.6064, -2.9805, 1.5110, 0.2880, 2.9443, -0.3807, -1.8105, 0.5158, 1.0976, 0.8062))
  I2m=np.minimum(a[8]*(I2/a[8])**((min(G/a[9],1))**a[10]),0.572)
  xc=(np.exp(1.0/(1+np.exp(a[0]+a[1]*G))+a[2]/(I2m+1)+a[3])*(rv70+a[4])*hfg**a[5]+a[6]*rv70)*np.exp(a[7]*R)
  #xc=(np.exp(1.0/(1+np.exp(a[0]+a[1]*G))+a[2]/(I2m+1)+a[3])*(rv70+a[4])*hfg**a[5]+a[6]*rv70)*np.exp(a[7])
  #print "I2m: " + str(I2m)
  return xc
  
def norm_sub(sub_bundle):
  """ normalizes subbundle """
  ut = np.array(sub_bundle)
  for i in range(sub_bundle.shape[0]):
    a = np.sum(sub_bundle[i,:,:])        # sum av nodplan 
    b = np.sum(sub_bundle[i,:,:]>0.0001) # antal bränslestavar i nodplanet
    ut[i,:,:] = sub_bundle[i,:,:]/a*b    # normerat bränsleplan
  return ut

if __name__ == '__main__':
  POW3 = sys.argv[1]
  btf_opt3(POW)
  
