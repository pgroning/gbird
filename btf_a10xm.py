from IPython.core.debugger import Tracer
import time

import numpy as np
import sys

from lib.libADDC import ADDC
#sys.path.append('lib/')
#import libADDC
#from addc import addc
        

def rfact_axial(POW, fuetype):
    """Calculating axial R-factors"""
    
    # Import addc from shared lib
    acObj = ADDC(fuetype)
    AC = acObj.ac
    
    # Define some matrix dimensions
    nside = AC.shape[0]  # Number of side pins of the assembly
    dim = nside + 2  # Pin map storage dimension

    Ntotrods = 100  # Total number of rods for ATRIUM 10XM
    # Calculate number of hot rods (POW[i,j] > 0)
    Nhotrods = sum(sum(POW > 0))  # Number of hot rods

    # Determine total power
    FBUN = sum(sum(POW))

    # Calculate local peaking distribution
    POD = POW/FBUN * Nhotrods
    
    # Calculate square root of power
    RP = np.zeros((dim, dim), dtype=float)
    RP[1:nside+1,1:nside+1] = np.sqrt(POD)
    
    # Define Rod Weight factors
    WP = np.zeros((dim, dim), dtype=float)
    # Considered rod: wp = 1. wp(unheated rod) = 0.25 x wp(heated rod)
    #WP2 = np.zeros((dim, dim), dtype=float)
    WP[1:nside+1, 1:nside+1] = (POD > 0.0001).astype(float)
    WP[1:nside+1, 1:nside+1] += 0.25 * (POD < 0.0001).astype(float)
    #for i in range(1,nside+1):
    #    for j in range(1,nside+1):
    #        if POD[i-1,j-1] > 0.0001:
    #            WP[i,j] = 1.0
    #        else:
    #            WP[i,j] = 0.25
    
    # Calculate pinwise R-factors for fuel-rods where POW > 0
    DOW = np.zeros((nside, nside), dtype=float)
    # Side rods
    WJ = 0.1   # Weighting factor for side neighboring rods
    WK = WJ/2  # Weighting factor for diagonal neighboring rods

    for i in range(1,nside+1):
        for j in range(1,nside+1):
            if POD[i-1,j-1] > 0.0001:
                # Side rods
                SJ1 = (RP[i-1,j]*WP[i-1,j] + RP[i+1,j]*WP[i+1,j] + 
                RP[i,j-1]*WP[i,j-1] + RP[i,j+1]*WP[i,j+1])*WJ

                SJ2 = (WP[i-1,j] + WP[i+1,j] +
                WP[i,j-1] + WP[i,j+1])*WJ*RP[i,j]

                SJ = min([SJ1,SJ2])

                # Diagonal rods
                SK1 = (RP[i-1,j-1]*WP[i-1,j-1] + RP[i+1,j-1]*WP[i+1,j-1] +
                RP[i-1,j+1]*WP[i-1,j+1] + RP[i+1,j+1]*WP[i+1,j+1])*WK

                SK2 = (WP[i-1,j-1] + WP[i+1,j-1] +
                WP[i-1,j+1] + WP[i+1,j+1])*WK*RP[i,j]

                SK = min([SK1,SK2])

                # Sum weighting factors
                # Side rods
                SWJ = (WP[i-1,j] + WP[i+1,j] + WP[i,j-1] + WP[i,j+1])*WJ
                # Diagonal rods
                SWK = (WP[i-1,j-1] + WP[i+1,j-1] + WP[i-1,j+1] + 
                       WP[i+1,j+1])*WK

                DOW[i-1,j-1] = (((RP[i,j] + SJ + SK)/(1.0 + SWJ + SWK)*
                                 np.sqrt(Ntotrods/float(Nhotrods))) + 
                                AC[i-1,j-1])
    
    return DOW


def btf_a10xm(POW3, fuetype):
    """Calculating BTF for A10XM"""

    naxial_nodes = POW3.shape[0]
    nrows = POW3.shape[1]
    ncols = POW3.shape[2]

    # Init array
    DOW = np.zeros((naxial_nodes, nrows, ncols), dtype=float)
    
    # Calculate lattice K-factors for all nodes
    # Check if old axial rfact calculation can be re-used
    for node in xrange(naxial_nodes):
        if (node > 0) and (POW3[node, :, :] == POW3[node-1, :, :]).all():
            DOW[node, :, :] = DOW[node-1, :, :]
        else:  # Perform new calculation
            DOW[node, :, :] = rfact_axial(POW3[node, :, :], fuetype)

    # Integrate along z-direction to get pinwise R-factors
    DOX = sum(DOW, 0)/naxial_nodes

    return DOX

if __name__ == '__main__':
    casobj = casio()
    casobj.loadpic('caxfiles_a10xm.p')
    POW3 = casobj.pow3(casobj)
