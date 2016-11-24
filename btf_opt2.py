from IPython.core.debugger import Tracer

import numpy as np
import sys

#from casio import casio
#from casdata_pts_2 import casdata

#sys.path.append('lib/')
#import libADDC
#from addc import addc
       

def acc_weifun(x):
    if x <= 0.06:
        f = 0.0
    elif x <= 0.279:
        f = -0.201924 + 3.40947*x - 12.3305*x**3 + 24.486*x**5
    elif x <= 0.96:
        f = 0.332027 + 0.684359*x
    else:
        f = 1.0
    return f

def node_weight(z, naxial_nodes):
    x1 = 1 - (z - 1)/float(naxial_nodes)
    x2 = 1 - z/float(naxial_nodes)
    f1 = acc_weifun(x1)
    f2 = acc_weifun(x2)
    wz = f1 - f2
    return wz

def rfact_axial(fuetype,POW):
    # Calculating axial R-factor
    
    # Import addc from shared lib
    #print fuetype
    acObj = libADDC.addc(fuetype)
    AC = acObj.addc
    #AC,dim = libADDC.addc(fuetype)
    #AC = AC[:dim,:dim]

    # Define some matrices
    nside = AC.shape[0] # Number of side pins of the assembly
    dim = nside + 2 # Pin map storage dimension

    # Calculate number of hot rods (POW[i,j] > 0)
    Ntotrods = 96 # Total number of rods for SVEA-96
    Nhotrods = sum(sum(POW>0)) # Number of hot rods

    # Determine total power for each sub bundle
    FSUB = np.zeros(4)
    FSUB[0] = sum(sum(POW[:5,:5])) # North-West quarter
    FSUB[1] = sum(sum(POW[6:,:5])) # South-West
    FSUB[2] = sum(sum(POW[:5,6:])) # North-East
    FSUB[3] = sum(sum(POW[6:,6:])) # South-East
    
    # Normalized sub bundle power distribution
    POD = np.zeros(POW.shape)
    POD[:5,:5] = POW[:5,:5]/FSUB[0] * Nhotrods/4
    POD[6:,:5] = POW[6:,:5]/FSUB[1] * Nhotrods/4
    POD[:5,6:] = POW[:5,6:]/FSUB[2] * Nhotrods/4
    POD[6:,6:] = POW[6:,6:]/FSUB[3] * Nhotrods/4

    #FSUB = FSUB/FSUB.mean()
    # Calculate mismatch-factor
    #MF = -0.14 + 1.5*FSUB - 0.36*FSUB**2

    # Calculate square root of power
    RP = np.zeros((dim,dim))
    RP[1:nside+1,1:nside+1] = np.sqrt(POD)
    
    # Define Rod Weight factors
    WP = np.zeros((dim,dim))
    #WP[1:nside+1,1:nside+1] = np.ones((nside,nside))
    # Water cross/channel
    for i in range(1,nside+1):
        for j in range(1,nside+1):
            if POD[i-1,j-1] > 0.0001:
                WP[i,j] = 1.0

    # PLR (modeled as cold rods)
    # For cold rods the weighting factor is 0.25 of the value of heated rod in that position
    # PLR (1/3)
    if POD[0,0]   < 0.0001: WP[1,1]   = 0.25
    if POD[0,10]  < 0.0001: WP[1,11]  = 0.25
    if POD[10,0]  < 0.0001: WP[11,1]  = 0.25
    if POD[10,10] < 0.0001: WP[11,11] = 0.25
    # PLR (2/3)
    if POD[3,4]   < 0.0001: WP[4,5]   = 0.25
    if POD[4,3]   < 0.0001: WP[5,4]   = 0.25
    if POD[3,6]   < 0.0001: WP[4,7]   = 0.25
    if POD[4,7]   < 0.0001: WP[5,8]   = 0.25   
    if POD[6,3]   < 0.0001: WP[7,4]   = 0.25
    if POD[7,4]   < 0.0001: WP[8,5]   = 0.25
    if POD[6,7]   < 0.0001: WP[7,8]   = 0.25
    if POD[7,6]   < 0.0001: WP[8,7]   = 0.25

    # Calculate pinwise R-factors for fuel-rods where POW > 0
    DOW = np.zeros((nside,nside))
    # Side rods
    WJ = 0.25  # Weighting factor for side neighboring rods
    WK = 0.125 # Weighting factor for diagonal neighboring rods
    for i in range(1,nside+1):
        for j in range(1,nside+1):
            if POD[i-1,j-1] > 0.0001:
            #if RP[i,j] > 0:
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
                SWJ = (WP[i-1,j] + WP[i+1,j] + WP[i,j-1] + WP[i,j+1])*WJ # Side rods
                SWK = (WP[i-1,j-1] + WP[i+1,j-1] + WP[i-1,j+1] + WP[i+1,j+1])*WK # Diagonal rods

                DOW[i-1,j-1] = (RP[i,j] + SJ + SK)/(1.0 + SWJ + SWK)*np.sqrt(Ntotrods/float(Nhotrods)) + AC[i-1,j-1]
                

    # Apply corner rod protection.
    # The R-factor should be increased about half of the desired CPR correction
    #crpfact = 0.02
    #DOW[0,0] = DOW[0,0]                         * (1.0 + crpfact*0.5)
    #DOW[0,nside-1] = DOW[0,nside-1]             * (1.0 + crpfact*0.5)
    #DOW[nside-1,0] = DOW[nside-1,0]             * (1.0 + crpfact*0.5)
    #DOW[nside-1,nside-1] = DOW[nside-1,nside-1] * (1.0 + crpfact*0.5)

    # Calculate the max R-factor for the assembly
    #Rfact = DOW.max()
    return DOW


def btf_opt2(POW3):
    """Calculating BTF for OPT2"""

    naxial_nodes_flr = POW3.shape[0]  # Total number of axial nodes
    # Number of axial nodes for PLRs (Condition: P > 0 for a pin)
    # PLR (1/3)
    naxial_nodes_plr1 = len([1 for POW2 in POW3 if POW2[0,10] > 0.0001])
    # PLR (2/3)
    naxial_nodes_plr2 = len([1 for POW2 in POW3 if POW2[3,4] > 0.0001])

    # naxial_nodes = 25      # Total number of nodes
    # naxial_nodes_plr1 = 9  # number of axial_nodes for 1/3 PLRs
    # naxial_nodes_plr2 = 17 # number of axial nodes for 2/3 PLRs

    # Setup rod maps
    nrows = POW3.shape[1]
    ncols = POW3.shape[2]
    M_plr1 = np.zeros((nrows, ncols), dtype=int)  # PLR (1/3) map
    M_plr1[0, 0] = M_plr1[0, 10] = M_plr1[10, 0] = M_plr1[10, 10] = 1

    M_plr2 = np.zeros((nrows, ncols), dtype=int)  # PLR (2/3) map
    M_plr2[3, 4] = M_plr2[4, 3] = M_plr2[3, 6] = M_plr2[6, 3] = 1
    M_plr2[4, 7] = M_plr2[7, 4] = M_plr2[6, 7] = M_plr2[7, 6] = 1

    M_flr = 1 - M_plr1 - M_plr2  # FLR map
    
    # Init arrays
    nsubs = 4  # Number of sub bundles
    MF = np.zeros((naxial_nodes_flr, nsubs), dtype=float)
    MFQ = np.zeros((nrows/2, ncols/2), dtype=float)
    DOW = np.zeros((naxial_nodes_flr, nrows, ncols), dtype=float)
    DOX = np.zeros((nrows, ncols), dtype=float)
    WZ = np.zeros(naxial_nodes_flr, dtype=float)
    FSUB = np.zeros(nsubs, dtype=float)
    Raxw = np.zeros((nrows, ncols))
    MFpl = np.zeros(nsubs)

    # Total number of rods (POW3[0,i,j] > 0)
    Ntotrods = sum(sum(POW3[0, :, :] > 0.0001))

    for node in xrange(naxial_nodes_flr):
        
        # Total number of hot rods (POW[i,j] > 0)
        Nhotrods = sum(sum(POW3[node, :, :] > 0.0001))
        
        # *****Mismatch factor calculation*****
        
        # Determine total power for each sub bundle
        FSUB[0] = sum(sum(POW3[node, :5, :5])) # North-West quarter
        FSUB[1] = sum(sum(POW3[node, 6:, :5])) # South-West
        FSUB[2] = sum(sum(POW3[node, :5, 6:])) # North-East
        FSUB[3] = sum(sum(POW3[node, 6:, 6:])) # South-East
        # Normalize sub-bundle power
        FSUB = FSUB/FSUB.mean()
        
        # Calculate mismatch-factor for each sub-bundle
        MF[node, :] = -0.14 + 1.5*FSUB - 0.36*FSUB**2
        
        # Calculate axial BTF
        # Check if old axial rfact calculation can be re-used 
        if (node > 0) and (POW3[node, :, :] == POW3[node-1, :, :]).all():
            DOW[node, :, :] = DOW[node-1, :, :]
        else:  # Perform new calculation
            print node
            DOW[node, :, :] = np.ones((nrows, ncols))  # only for testing
            DOW[node, 5, :] = 0
            DOW[node, :, 5] = 0
            #DOW[z,:,:] = rfact_axial(fuetype,POW3[z,:,:])
        WZ[node] = node_weight(node + 1, naxial_nodes_flr)
    
    # Apply mismatch-factor to FLRs only (PLRs are taken care of separately)
    for node in xrange(naxial_nodes_flr):
        # North-West
        MFQ = M_flr[:5, :5] * (MF[node, 0] - 1) + 1
        DOW[node, :5, :5] = DOW[node, :5, :5] * MFQ
        # South-West
        MFQ = M_flr[6:, :5] * (MF[node, 1] - 1) + 1
        DOW[node, 6:, :5] = DOW[node, 6:, :5] * MFQ
        # North-East
        MFQ = M_flr[:5, 6:] * (MF[node, 2] - 1) + 1
        DOW[node, :5, 6:] = DOW[node, :5, 6:] * MFQ
        # South-East
        MFQ = M_flr[6:, 6:] * (MF[node, 3] - 1) + 1
        DOW[node, 6:, 6:] = DOW[node, 6:, 6:] * MFQ

    '''
    for node in xrange(naxial_nodes_flr):
        for i in xrange(nrows):
            for j in xrange(ncols):
                if M_flr[i, j]:  # check if pin at position (i,j) is FLR
                    if i < 5 and j < 5:     # North-West
                        mf = MF[node, 0]
                    elif i < 11 and j < 5:  # South-West
                        mf = MF[node, 1]
                    elif i < 5 and j < 11:  # North-East
                        mf = MF[node, 2]
                    elif i < 11 and j < 11: # South-East
                        mf = MF[node, 3]
                    DOW[node, i, j] = DOW[node, i, j] * mf
       '''
        # Apply axial weight function
        # WZ[z-1] = node_weight(z,naxial_nodes)
        # Raxw += DOW*WZ

    # Apply average mismatch-factor (along axial-direction) for PLRs
    MF_plr = MF.mean(0)  # Take average along axial-direction
    M_plr = M_plr1 + M_plr2

    MFQ1 = M_plr[:5, :5] * (MF_plr[0] - 1) + 1
    MFQ2 = M_plr[6:, :5] * (MF_plr[1] - 1) + 1
    MFQ3 = M_plr[:5, 6:] * (MF_plr[2] - 1) + 1
    MFQ4 = M_plr[6:, 6:] * (MF_plr[3] - 1) + 1
    for node in xrange(naxial_nodes_flr):
        # North-West
        DOW[node, :5, :5] = DOW[node, :5, :5] * MFQ1
        # South-West
        DOW[node, 6:, :5] = DOW[node, 6:, :5] * MFQ2
        # North-East
        DOW[node, :5, 6:] = DOW[node, :5, 6:] * MFQ3
        # South-East
        DOW[node, 6:, 6:] = DOW[node, 6:, 6:] * MFQ4

    '''
    for z in range(naxial_nodes):
        for i in range(DOW[0][0].size):
            for j in range(DOW[0][1].size):
                if Mplr[i,j]:
                    if i<5 and j<5    : mf = MFpl[0]
                    elif i<11 and j<5 : mf = MFpl[1]
                    elif i<5 and j<11 : mf = MFpl[2]
                    elif i<11 and j<11: mf = MFpl[3]
                    DOW[z,i,j] = DOW[z,i,j] * mf
    '''

    # Integrate along z-direction and apply axial weight function to get
    # pinwise R-factors
    # DOX = np.zeros(DOW[0].shape)
    frac1 = 0.425
    frac2 = 0.25
    
    #frac1 = 0.337*naxial_nodes - naxial_nodes_plr1
    #frac2 = 0.65*naxial_nodes - naxial_nodes_plr2
    for node in xrange(naxial_nodes_flr):
        if node < (naxial_nodes_plr1 - 1):  # All rods present
            DOX += DOW[node, :, :] * WZ[node]
        elif node < (naxial_nodes_plr2 - 1):  # 2/3 PLR + FLR rods present
            DOX += DOW[node, :, :] * WZ[node] * (1 - M_plr1)
            #for i in range(DOX.shape[0]):
            #    for j in range(DOX.shape[1]):
            #        if not Mplr1[i,j]:
            #            DOX[i,j] += DOW[node, i, j] * WZ[node]
        else:  # only FLR rods present
            DOX += DOW[node, :, :] * WZ[node] * M_flr
            #for i in range(DOX.shape[0]):
            #    for j in range(DOX.shape[1]):
            #        if Mflr[i,j]:
            #            DOX[i,j] += DOW[z,i,j]*WZ[z]
        
        # Account for the fact that the heated length top part of PLRs is
        # within the node.
        if node == (naxial_nodes_plr1 - 1):  # 1/3 PLR is within the node
            DOX += DOW[node, :, :] * WZ[node] * M_plr1 * frac1
            #for i in range(DOX.shape[0]):
            #    for j in range(DOX.shape[1]):
            #        if Mplr1[i,j]:
            #            DOX[i,j] += DOW[z,i,j]*WZ[z]*frac1
            
        if node == (naxial_nodes_plr2 - 1):  # 2/3 PLR is within the node
            DOX += DOW[node, :, :] * WZ[node] * M_plr2 * frac2
            #for i in range(DOX.shape[0]):
            #    for j in range(DOX.shape[1]):
            #        if Mplr2[i,j]:
            #            DOX[i,j] += DOW[z,i,j]*WZ[z]*frac2

    return DOX

if __name__ == '__main__':
    casobj = casio()
    casobj.loadpic('caxfiles.p')
    POW3 = pow3d(casobj)
    #Tracer()()
