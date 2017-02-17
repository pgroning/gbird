#!/usr/bin/env python

# Run from ipython:
# > from casdata import casdata
# > case = casdata('caxfile')
#
# or:
# run casdata "caxfile"
#
# How to reach name mangling ("private") methods:
# self._Segment__matchcontent()
#

# For debugging. Add Tracer()() inside the code to break at that line
from IPython.core.debugger import Tracer
# Inside iptyhon shell: run -d b<L> readfile.py
# sets a break point add line L.

import numpy as np
import re
import linecache
import os
import sys
import time
from subprocess import call, STDOUT
import uuid  # used for random generated file names
import shlex  # used for splitting subprocess call argument string into a list

'''
#from multiprocessing import Pool
#from btf import btf
#from pyqt_trace import pyqt_trace
'''


class DataStruct(object):
    """Initialize a class that can be used to structure data"""
    pass


class Segment(object):

    def __init__(self, caxfile=None, read_all=False):
        self.data = DataStruct()
        #self.states = []
        #self.states.append(DataStruct())
        # self.add_calc()
        # self.states[0].refcalc = DataStruct()
        # Tracer()()
        '''
        #self.data.append(DataStruct()) # Add an element to list
        #self.data[-1]
        #self.statepts = []
        #self.pert = DataStruct()
        '''
        if caxfile:
            self.readcax(caxfile, read_all)
            self.ave_enr_calc()
            # self.quickcalc(refcalc=True)
            # self.btfcalc()

    # -------Read cax file---------
    def __matchcontent(self, flines, regexp, opt='all'):
        rec = re.compile(regexp)
        if opt == 'all':
            out = [i for i, x in enumerate(flines) if rec.match(x)]
        elif opt == 'next':
            out = next(i for i, x in enumerate(flines) if rec.match(x))
        elif opt == 'object':
            out = (i for i, x in enumerate(flines) if rec.match(x))
        return out

    def __symmap(self, lines, npst, dtype=float):
        M = self.__symtrans(self.__map2mat(lines, npst)).astype(dtype)
        return M

    def __get_FUE(self, flines, iFUE):
        Nfue = len(iFUE)
        FUE = np.zeros((Nfue, 5))
        FUE.fill(np.nan)
        for i, idx in enumerate(iFUE):
            rstr = flines[idx].replace(',', ' ').strip()
            rstr = rstr.replace('/', ' ').strip()
            rstr = rstr.replace('=', ' ').strip()
            rvec = re.split('\*', rstr, 1)  # split on first occurence
            rstr = rvec[0].strip()
            rvec = re.split('\s+', rstr)
            FUE[i, :len(rvec[1:])] = rvec[1:]
        return FUE

    def __get_pin(self, flines, iPIN):
        plist = []
        for idx in iPIN:
            rstr = flines[idx].replace(',', ' ').strip()
            rvec = re.split('/|\*', rstr)
            rstr = rvec[0].strip()
            rvec = re.split('\s+', rstr.strip())
            rlen = np.size(rvec)
            plist.append(rvec[1:])

        Npin = len(plist)
        ncols = max(map(len, plist))
        PIN = np.zeros((Npin, ncols), dtype=float)
        PIN.fill(np.nan)
        for i, pl in enumerate(plist):
            PIN[i, :len(pl)] = pl
        return PIN

    def __lfu2enr(self, LFU, FUE):
        ENR = np.zeros(LFU.shape)
        Nfue = FUE.shape[0]
        for i in range(Nfue):
            ifu = int(FUE[i, 0])
            ENR[LFU == ifu] = FUE[i, 2]
        return ENR

    def __lfu2ba(self, LFU, FUE):
        BA = np.zeros(LFU.shape)
        Nfue = FUE.shape[0]
        for i in range(Nfue):
            ifu = int(FUE[i, 0])
            if np.isnan(FUE[i, 3]):
                BA[LFU == ifu] = 0.0
            else:
                BA[LFU == ifu] = FUE[i, 4]
        return BA

    def readcax(self, caxfile, read_all=False):

        if not os.path.isfile(caxfile):
            print "Could not open file " + caxfile
            return
        else:
            print "Reading file " + caxfile
        '''
        # Read input file up to maxlen using random access
        #maxlen = 100000
        #flines = []
        #for i in range(maxlen):
        #    flines.append(linecache.getline(caxfile,i+1).rstrip())
        '''
        # Read the whole file
        with open(caxfile) as f:
            # flines = f.readlines() # include \n
            flines = f.read().splitlines()  # exclude \n
        '''
        # Define regexps
        #reS3C = re.compile('(^| )S3C')
        #reITTL = re.compile('^\*I TTL')
        #reREA = re.compile('REA\s+')
        #reGPO = re.compile('GPO\s+')
        '''
        # Search for regexp matches
        # self.__flines = flines

        # Find last index containing voids voi=vhi
        tmp_voilist = []  # temporary list of voids
        # if read_content != 'all':
        oTIT = self.__matchcontent(flines, '^TIT', 'object')
        while True:
            try:
                i = oTIT.next()
            except:  # Reaching end of flines
                break
                # split on spaces or '/'
            rstr = re.split('[/\s+]+', flines[i+2].strip())
            voi, vhi = rstr[1], rstr[2]
            if voi != vhi:
                break
            tmp_voilist.append(voi)
        # Reduce to a unique list and also keep the order
        tmp = []
        tmp_voilist = [x for x in tmp_voilist if x not in tmp and (tmp.append(x)
                                                                   or True)]
        voilist = map(int, map(float, tmp_voilist))

        if not read_all:
            flines = flines[:i]  # Reduce the number of lines in list

        # Search for regexp matches
        print "Scanning file content..."
        '''
        # Loop through the whole file content
        #reglist = ['^TIT','^\s*FUE\s+']
        #self.__flines = flines
        #n = 2
        #p = Pool(n)
        #ilist = p.map(self.__matchcontent, reglist)
        #p.close()
        #p.join()
        '''
        iTIT = self.__matchcontent(flines, '^TIT')
        iFUE = self.__matchcontent(flines, '^\s*FUE')
        iPOW = self.__matchcontent(flines, 'POW\s+')
        iSIM = self.__matchcontent(flines, '^\s*SIM')
        iSPA = self.__matchcontent(flines, '^\s*SPA')
        iGAM = self.__matchcontent(flines, '^\s*GAM')
        iCRD = self.__matchcontent(flines, '^\s*CRD')
        iPOL = self.__matchcontent(flines, '^POL')
        iXFL = self.__matchcontent(flines, '^XFL')
        iPIN = self.__matchcontent(flines, '^\s*PIN')
        iTTL = self.__matchcontent(flines, '^\s*TTL')
        iVOI = self.__matchcontent(flines, '^\s*VOI')
        iDEP = self.__matchcontent(flines, '^\s*DEP')

        # Stop looping at first finding
        iEND = self.__matchcontent(flines, '^\s*END', 'next')
        iBWR = self.__matchcontent(flines, '^\s*BWR', 'next')
        iLFU = self.__matchcontent(flines, '^\s*LFU', 'next')
        iLPI = self.__matchcontent(flines, '^\s*LPI', 'next')
        iTFU = self.__matchcontent(flines, '^\s*TFU', 'next')
        iTMO = self.__matchcontent(flines, '^\s*TMO', 'next')
        iPDE = self.__matchcontent(flines, '^\s*PDE', 'next')
        try:  # Card for water cross (valid for OPT2/3)
            iSLA = self.__matchcontent(flines, '^\s*SLA', 'next')
        except:
            iSLA = None
            # print "Info: Could not find SLA card"
        iWRI = self.__matchcontent(flines, '^\s*WRI', 'next')
        iSTA = self.__matchcontent(flines, '^\s*STA', 'next')
        print "Done."

        #do = DataStruct()  # Init data container object
        # Read title
        self.data.title = flines[iTTL[0]]
        #do.title = flines[iTTL[0]]
        # SIM
        self.data.sim = flines[iSIM[0]]
        #do.sim = flines[iSIM[0]]
        # TFU
        self.data.tfu = flines[iTFU]
        #do.tfu = flines[iTFU]
        # TMO
        self.data.tmo = flines[iTMO]
        #do.tmo = flines[iTMO]
        # VOI
        self.data.voi = flines[iVOI[0]]
        #do.voi = flines[iVOI[0]]
        # PDE
        self.data.pde = flines[iPDE]
        #do.pde = flines[iPDE]
        # BWR
        self.data.bwr = flines[iBWR]
        #do.bwr = flines[iBWR]
        # SPA
        self.data.spa = flines[iSPA[0]]
        #do.spa = flines[iSPA[0]]
        # DEP
        self.data.dep = flines[iDEP[0]]
        #do.dep = flines[iDEP[0]]
        # GAM
        self.data.gam = flines[iGAM[0]]
        #do.gam = flines[iGAM[0]]
        # WRI
        self.data.wri = flines[iWRI]
        #do.wri = flines[iWRI]
        # STA
        self.data.sta = flines[iSTA]
        #do.sta = flines[iSTA]
        # CRD
        self.data.crd = flines[iCRD[0]]
        #do.crd = flines[iCRD[0]]

        # get fuel dimension
        npst = int(flines[iBWR][5:7])
        # Read LFU map
        maplines = flines[iLFU+1:iLFU+1+npst]
        # LFU = self.__symtrans(self.__map2mat(caxmap, npst)).astype(int)
        LFU = self.__symmap(maplines, npst, int)
        # LFU = self.__symmetry_map(flines, iLFU, npst)

        # Read LPI map
        maplines = flines[iLPI+1:iLPI+1+npst]
        # LPI = self.__symtrans(self.__map2mat(caxmap, npst)).astype(int)
        LPI = self.__symmap(maplines, npst, int)
        # LPI = self.__symmetry_map(flines, iLPI, npst)

        # Get FUE array
        iFUE = [i for i in iFUE if i < iEND]
        FUE = self.__get_FUE(flines, iFUE)

        # Translate LFU map to ENR map
        ENR = self.__lfu2enr(LFU, FUE)

        # Translate LFU map to BA map
        BA = self.__lfu2ba(LFU, FUE)

        # Determine number of BA rods types
        Nba = 0
        for content in FUE[:, 4]:
            if not np.isnan(content):
                Nba += 1

        # Read PIN (pin radius)
        PIN = self.__get_pin(flines, iPIN)

        Npin = PIN.shape[0]
        # self.pinlines = flines[iPIN[0]:iPIN[0]+Npin]
        self.data.pinlines = flines[iPIN[0]:iPIN[0]+Npin]

        # Read SLA
        if iSLA is not None:
            self.data.slaline = flines[iSLA]

        # ------Step through the state points----------
        print "Scanning state points..."

        # Tracer()()
        # Nburnpts = iTIT.size
        Nburnpts = len(iTIT)
        # titcrd = []
        burnup = np.zeros(Nburnpts)
        burnup.fill(np.nan)
        voi = np.zeros(Nburnpts)
        voi.fill(np.nan)
        vhi = np.zeros(Nburnpts)
        vhi.fill(np.nan)
        tfu = np.zeros(Nburnpts)
        tfu.fill(np.nan)
        tmo = np.zeros(Nburnpts)
        tmo.fill(np.nan)
        kinf = np.zeros(Nburnpts)
        kinf.fill(np.nan)
        POW = np.zeros((npst, npst, Nburnpts))
        POW.fill(np.nan)
        XFL1 = np.zeros((npst, npst, Nburnpts))
        XFL1.fill(np.nan)
        XFL2 = np.zeros((npst, npst, Nburnpts))
        XFL2.fill(np.nan)

        # Read title cards
        titcrd = [flines[i] for i in iTIT]

        # Row vector containing burnup, voi, vhi, tfu and tmo
        # rvec = [re.split('/',flines[i+2].strip()) for i in iTIT]
        # rvec = [re.split('[/\s+]+', flines[i+2].strip()) for i in iTIT]

        # Row containing Kinf
        # kinfstr = [flines[i+5] for i in iPOL]

        # Rows containing radial power distribution map
        # powmap = [flines[i+2:i+2+npst] for i in iPOW]

        # Rows containing XFL maps
        # xfl1map = [flines[i+2:i+2+npst] for i in iXFL]
        # xfl2map = [flines[i+3+npst:i+3+2*npst] for i in iXFL]

        for i in range(Nburnpts):
            # Read burnup, voids, tfu and tmo
            rvec = re.split('[/\s+]+', flines[iTIT[i]+2].strip())
            burnup[i] = rvec[0]
            voi[i] = rvec[1]
            vhi[i] = rvec[2]
            tfu[i] = rvec[3]
            tmo[i] = rvec[4]
            # burnup[i],voi[i] = re.split('\s+',rvec[i][0].strip())
            # vhi[i],tfu[i] = re.split('\s+',rvec[i][1].strip())
            # tmo[i] = re.split('\s+',rvec[i][2].strip())[1]
            # Read kinf
            kinfstr = flines[iPOL[i]+5]
            kinf[i] = re.split('\s+', kinfstr.strip())[0]
            # Read radial power distribution map
            powlines = flines[iPOW[i]+2:iPOW[i]+2+npst]
            POW[:, :, i] = self.__symmap(powlines, npst)
            # POW[:, :, i] = self.__symtrans(self.__map2mat(powmap[i], npst))
            # Read XFL maps
            if iXFL:  # check if XFL exists
                xfl1lines = flines[iXFL[i]+2:iXFL[i]+2+npst]
                XFL1[:, :, i] = self.__symmap(xfl1lines, npst)
                # XFL1[:, :, i] = (self.__symtrans(
                #        self.__map2mat(xfl1map[i], npst)))
                xfl2lines = flines[iXFL[i]+3+npst:iXFL[i]+3+2*npst]
                XFL2[:, :, i] = self.__symmap(xfl2lines, npst)
                # XFL2[:, :, i] = (self.__symtrans(
                #        self.__map2mat(xfl2map[i], npst)))
        print "Done."
        # --------------------------------------------------------------------
        # Calculate radial burnup distributions
        EXP = self.__expcalc(POW, burnup)
        # Calculate Fint:
        fint = self.__fintcalc(POW)

        # Append state instancies
        #do.statepoints = []
        self.statepoints = []
        for i in range(Nburnpts):
            # append new instance to list
            self.statepoints.append(DataStruct())
            #do.statepoints.append(DataStruct())
            self.statepoints[i].titcrd = titcrd[i]
            #do.statepoints[i].titcrd = titcrd[i]
            self.statepoints[i].burnup = burnup[i]
            #do.statepoints[i].burnup = burnup[i]
            self.statepoints[i].voi = voi[i]
            #do.statepoints[i].voi = voi[i]
            self.statepoints[i].vhi = vhi[i]
            #do.statepoints[i].vhi = vhi[i]
            self.statepoints[i].tfu = tfu[i]
            #do.statepoints[i].tfu = tfu[i]
            self.statepoints[i].tmo = tmo[i]
            #do.statepoints[i].tmo = tmo[i]
            self.statepoints[i].kinf = kinf[i]
            #do.statepoints[i].kinf = kinf[i]
            self.statepoints[i].fint = fint[i]
            #do.statepoints[i].fint = fint[i]
            self.statepoints[i].EXP = EXP[:, :, i]
            #do.statepoints[i].EXP = EXP[:, :, i]
            if iXFL:
                self.statepoints[i].XFL1 = XFL1[:, :, i]
                #do.statepoints[i].XFL1 = XFL1[:, :, i]
                self.statepoints[i].XFL2 = XFL2[:, :, i]
                #do.statepoints[i].XFL2 = XFL2[:, :, i]
            self.statepoints[i].POW = POW[:, :, i]
            #do.statepoints[i].POW = POW[:, :, i]

        # Saving geninfo
        self.data.caxfile = caxfile
        #do.caxfile = caxfile
        self.data.ENR = ENR
        #do.ENR = ENR
        self.data.BA = BA
        #do.BA = BA
        self.data.PIN = PIN
        #do.PIN = PIN
        self.data.LPI = LPI
        #do.LPI = LPI
        self.data.FUE = FUE
        #do.FUE = FUE
        self.data.LFU = LFU
        #do.LFU = LFU
        self.data.npst = npst
        #do.npst = npst
        self.data.voilist = voilist
        #do.voivec = voivec
        # Append data object to last list element
        #self.states[-1] = do
        #self.data = do

    def __map2mat(self, caxmap, dim):
        M = np.zeros((dim, dim))
        M.fill(np.nan)
        for i in range(dim):
            rstr = caxmap[i]
            rvec = re.split('\s+', rstr.strip())
            M[i, 0:i+1] = rvec
        return M

    def __symtrans(self, M):
        Mt = M.transpose()
        dim = M.shape[0]
        for i in range(1, dim):
            Mt[i, 0:i] = M[i, 0:i]
        return Mt

    # --------Calculate average enrichment----------
    def ave_enr_calc(self, LFU=None, FUE=None):

        # Inargs: FUE, LFU
        
        # Translate LFU map to DENS and ENR map
        npst = self.data.npst
        DENS = np.zeros((npst, npst))
        ENR = np.zeros((npst, npst))
        if LFU is None:
            LFU = self.data.LFU
        if FUE is None:
            FUE = self.data.FUE
        Nfue = FUE[:, 0].size
        for i in range(Nfue):
            ifu = int(FUE[i, 0])
            DENS[LFU == ifu] = FUE[i, 1]
            ENR[LFU == ifu] = FUE[i, 2]
        
        # Translate LPI map to pin radius map
        RADI = np.zeros((npst, npst))
        LPI = self.data.LPI
        PIN = self.data.PIN
        Npin = PIN[:, 0].size
        for i in range(Npin):
            ipi = int(PIN[i, 0])
            RADI[LPI == ipi] = PIN[i, 1]
        
        # Calculate mass
        VOLU = np.pi*RADI**2
        MASS = DENS*VOLU
        mass = np.sum(MASS)
        MASS_U235 = MASS*ENR
        mass_u235 = np.sum(MASS_U235)
        self.data.ave_enr = mass_u235/mass

    # -------Write cai file------------
    def writecai(self, file_base_name):
        # print "Writing to file " + caifile

        cainp = file_base_name + ".inp"
        print "Writing C input file " + cainp

        info = self.states[0]
        f = open(cainp, 'w')
        f.write(info.title + '\n')
        f.write(info.sim + '\n')
        f.write(info.tfu + '\n')
        f.write(info.tmo + '\n')
        f.write(info.voi + '\n')

        Nfue = info.FUE.shape[0]
        for i in range(Nfue):
            f.write(' FUE  %d ' % (info.FUE[i, 0]))
            f.write('%5.3f/%5.3f' % (info.FUE[i, 1], info.FUE[i, 2]))
            if ~np.isnan(info.FUE[i, 3]):
                f.write(' %d=%4.2f' % (info.FUE[i, 3],
                                       info.FUE[i, 4]))
            f.write('\n')

        f.write(' LFU\n')
        for i in range(info.npst):
            for j in range(i+1):
                f.write(' %d' % info.LFU[i, j])
                # if j < i: f.write(' ')
            f.write('\n')

        f.write(info.pde + '\n')
        f.write(info.bwr + '\n')

        Npin = np.size(info.pinlines)
        for i in range(Npin):
            f.write(info.pinlines[i] + '\n')

        if hasattr(info, 'slaline'):
            f.write(info.slaline.strip() + '\n')

        f.write(' LPI\n')
        for i in range(info.npst):
            for j in range(i+1):
                f.write(' %d' % info.LPI[i, j])
                # if j < i: f.write(' ')
            f.write('\n')

        f.write(info.spa + '\n')
        f.write(info.dep + '\n')
        f.write(info.gam + '\n')
        f.write(info.wri + '\n')
        f.write(info.sta + '\n')

        f.write(' TTL\n')

        depstr = re.split('DEP', info.dep)[1].replace(',', '').strip()
        f.write(' RES,,%s\n' % (depstr))

        # f.write(' RES,,0 0.5 1.5 2.5 5.0 7.5 10.0 12.5 15.0 17.5 20.0 25
        # 30 40 50 60 70\n')
        f.write(info.crd + '\n')
        f.write(' NLI\n')
        f.write(' STA\n')
        f.write(' END\n')
        f.close()

    def runc4(self, file_base_name, neulib=False, grid=False):
        """Running C4 model"""
        c4inp = file_base_name + ".inp"
        # C4 executable
        c4exe = "cas4 -e"
        # c4exe = "/home/prog/prod/CMSCODES/bin/cas4 -e"
        # C4 version
        c4ver = "2.10.21P_VAT_1.3"
        # lib directory
        libdir = "/home/prog/prod/CMSCODES/CasLib/library/"
        # neulib
        if not neulib:
            neulib = "e4lbl70"

        cmd = ' -V ' + c4ver + ' -N ' + libdir + neulib + ' ' + c4inp
        arglist = shlex.split(c4exe + cmd)
        arglist = shlex.split('linrsh ' + c4exe + cmd)
        # specify grid que
        arglist.insert(1, '-q')
        arglist.insert(2, 'all.q@wrath,all.q@envy,all.q@pride')
        # arglist[0] = 'linrsh -q all.q@wrath'
        # Tracer()()
        # fout = open('c4.stdout', 'wb')
        fout = open('/dev/null', 'wb')
        print "Running c4 model"
        if grid:
            try:  # use linrsh if available
                call(arglist, stdout=fout, stderr=STDOUT, shell=False)
            except:
                print "Warning: Grid is not available on the system."
                call(arglist[3:], stdout=fout, stderr=STDOUT, shell=False)
        else:
            call(arglist[3:], stdout=fout, stderr=STDOUT, shell=False)
    
    def set_data(self, LFU=None, FUE=None, BA=None, voi=None, box_offset=0.0):
        """Append a list element to store result of new calculation"""

        # limit number of states to 4
        # 0=original, 1=reference, 2=previous, 3=current
        #if len(self.states) > 3:
        #    del self.states[2]
        #self.states.append(DataStruct())  # Add an new element to list
       
        if LFU is not None:
            self.data.LFU = LFU
        
        if FUE is not None:
            self.data.FUE = FUE
        
        if BA is not None:
            self.data.BA = BA
        
        if (LFU is not None) and (FUE is not None):
            ENR = np.zeros(LFU.shape)
            Nfue = FUE[:, 0].size
            for i in range(Nfue):
                ifu = int(FUE[i, 0])
                ENR[LFU == ifu] = FUE[i, 2]
            self.data.ENR = ENR
        
        if voi is not None:
            self.data.voilist = [int(voi)]
        
        self.data.box_offset = box_offset
        
        #
        #if voi is None:
        #    voivec = self.states[0].voivec
        #else:
        #    voivec = [int(voi)]
        #self.states[-1].voivec = voivec
        #
        #self.states[-1].box_offset = box_offset
    
    # def voivec(self):
    #    info = self.states[0]
    #    voids = (info.voi.split('*')[0].replace(',', ' ')
    #              .strip().split(' ')[1:])
    #    return voids

    def writec3cai(self, file_base_name, voi=None, maxdep=60, depthres=None,
                   box_offset=0.0):
        # filebasename = "./" + str(uuid.uuid4())
        c3inp = file_base_name + ".inp"
        # c3inp = tempfile.NamedTemporaryFile(dir='.',
        # prefix="c3_",suffix=".inp",delete=False)
        print "Writing c3 input file " + c3inp

        # Creating dep strings
        info = self.data
        #voivec = info.voivec
        # voivec = self.voivec()
        # voivec = (info.voi.split('*')[0].replace(',', ' ')
        #          .strip().split(' ')[1:])
        
        if voi:
            voilist = [int(voi)]
            self.data.voilist = voilist
        else:
            voilist = self.data.voilist
        
        #if voi is not None:
        #    if int(voi) in voivec:
        #        bp_voivec = [int(voi)]
        #    else:
        #        bp_voivec = [voivec[0]]  # get burn points from first void
        #else:
        #    bp_voivec = voivec
        
        #if voi is not None:
        #    voivec = [int(voi)]
        #    self.data.voivec = voivec

        if not maxdep:
            maxdep = 60

        burnlist = []
        for v in voilist:
            if depthres:
                dep_points = [0, 0.001, -depthres]
                dep_next = -dep_points[-1] + 10
                while dep_next < maxdep:
                    dep_points.append(dep_next)
                    dep_next += 10
                dep_points.append(maxdep)
            else:
                dep_points = [0, 0.001, -maxdep]
            burnlist.append(dep_points)
        
        #burnlist = []
        #for i, v in enumerate(bp_voivec):
        #    all_points = self.burnpoints(voi=int(v))
        #    
        #    if maxdep:
        #        red_points = [x for x in all_points if x <= maxdep]
        #        burnlist.append(red_points)
        #    elif depthres:
        #        lo_points = [x for x in all_points if x <= depthres]
        #        # reduce number of points by taking every 5:th step in list
        #        up_points = [x for x in all_points if x > depthres][5::5]
        #        # concatenate lists
        #        red_points = sum([lo_points, up_points], [])
        #        # make sure last point is included
        #        if red_points[-1] < all_points[-1]:
        #            red_points.append(all_points[-1])
        #        burnlist.append(red_points)
        #    else:
        #        burnlist.append(all_points)
        
        if hasattr(self.data, 'LFU'):
            LFU = self.data.LFU
        else:
            print "Error: LFU is missing."
            return
        
        f = open(c3inp, 'w')

        tit_1 = "TIT "
        # tit_2 = info.tfu.split('*')[0].replace(',', '=').strip() + " "
        tit_2 = re.sub('\s+=|=\s+|,', '=', info.tfu.split('*')[0]
                       .strip()) + " "
        # tit_3 = info.tmo.split('*')[0].replace(',', '=').strip() + " "
        tit_3 = re.sub('\s+|,', '=', info.tmo.split('*')[0].strip()) + " "
        tit = tit_1 + tit_2 + tit_3
        if voi is None:
            # voivec = info.voi.split('*')[0].replace(',', ' ')\
            #                                      .strip().split(' ')[1:]
            tit = tit + "VOI=" + str(voilist[0]) + " "
            ide = ["'BD" + str(x) + "'" for x in voilist]
            f.write(tit + "IDE=" + ide[0] + '\n')
        else:
            tit = tit + "VOI=" + str(voi) + " "
            f.write(tit + '\n')
        f.write(info.sim.strip() + '\n')
        
        FUE = info.FUE
        Nfue = FUE.shape[0]
        baid_offset = 0  # The same BA id must not occur more than once
        for i in xrange(Nfue):
            f.write('FUE  %d ' % (FUE[i, 0]))
            f.write('%5.3f/%5.3f' % (FUE[i, 1], FUE[i, 2]))
            if ~np.isnan(FUE[i, 3]):
                f.write(' %d=%4.2f' % (FUE[i, 3] + baid_offset, FUE[i, 4]))
                baid_offset += 1
            f.write('\n')

        f.write('LFU\n')
        for i in xrange(info.npst):
            for j in xrange(i+1):
                f.write('%d ' % LFU[i, j])
            f.write('\n')

        pde = info.pde.split('\'')[0]
        f.write(pde.strip() + '\n')
        
        # box corner radius (extra thickness). True for AT11
        # Tracer()()
        # if '/' in info.bwr:
        #    bwr = info.bwr.replace('/','//')  # a // is needed for C3
        
        if hasattr(self.data, 'box_offset'):
            box_offset = self.data.box_offset
        bwr = self.__boxbow(box_offset)
        
        #if box_offset:
        #    bwr = self.__boxbow(box_offset)
        #    # f.write(bwr + '\n')
        #else:
        #    bwr = info.bwr.strip()
        #    # f.write(info.bwr.strip() + '\n')

        # box corner radius (extra thickness). Valid for AT11
        if '/' in bwr:
            bwr = bwr.replace('/', '//')  # a // is needed for C3

        f.write(bwr + '\n')

        Npin = np.size(info.pinlines)
        for i in xrange(Npin):
            # Remove coments etc
            tmpstr = re.split('\*|/', info.pinlines[i].strip())[0]
            pinarr = re.split(',|\s+', tmpstr.strip())  # Split for segments
            npinsegs = len(pinarr)-2
            if npinsegs > 3:
                red_pinstr = ' '.join(pinarr[0:3]+pinarr[-2:])
            else:
                red_pinstr = info.pinlines[i].strip()
            f.write(red_pinstr.strip() + '\n')
        
        if hasattr(info, 'slaline'):  # has water cross?
            if info.slaline:  # check that it is not empty
                f.write(info.slaline.strip() + '\n')
        
        f.write('LPI\n')
        for i in xrange(info.npst):
            for j in xrange(i+1):
                f.write('%d ' % info.LPI[i, j])
            f.write('\n')

        f.write(info.spa.strip() + '\n')
        
        f.write("DEP" + '\n')
        for x in burnlist[0]:
            f.write(str(x) + '\n')
        # if maxdep is None:
        #    f.write(info.dep.strip() + '\n')
        # else:
        #    depstr = "DEP 0, 0.001, -" + str(maxdep)
        #    f.write(depstr + '\n')
        
        f.write('NLI\n')
        f.write('STA\n')

        if voi is None:
            N = len(ide)
            for i in xrange(1, N):
                f.write("TIT " + "IDE=" + ide[i] + '\n')
                # f.write(tit + "IDE=" + ide[i] + '\n')
                res = "RES," + ide[i-1] + ",0"
                f.write(res + '\n')
                f.write("VOI " + str(voilist[i]) + '\n')

                f.write("DEP" + '\n')
                for x in burnlist[i]:
                    f.write(str(x) + '\n')

                # if maxdep is None:
                #    f.write(info.dep.strip() + '\n')
                # else:
                #    depstr = "DEP 0, 0.001, -" + str(maxdep)
                #    f.write(depstr + '\n')

                f.write('STA\n')

        f.write('END\n')
        # c3inp.close()
        f.close()
        # return filebasename

    def runc3(self, filebasename, grid=False):
        """Running C3 perturbation model"""
        
        # C3 input file
        c3inp = filebasename + ".inp"
        # c3inp = "./c3.inp"
        # output file
        # c3out = tempfile.NamedTemporaryFile(
        # dir='.',prefix="c3_",suffix=".out",delete=False)
        c3out = filebasename + ".out"
        # cax file
        c3cax = filebasename + ".cax"
        # C3 libs
        lib1 = "./lib/c3/e4lbj40"
        lib2 = "./lib/c3/bal8ab4"
        lib3 = "./lib/c3/galb410"
        # C3 executable
        c3exe = "./bin/casmo3"
        if os.path.isfile(c3exe):
            pass  # no need to change the location of executable and libs
        elif os.path.isfile("." + c3exe):
            c3exe = "." + c3exe
            lib1 = "." + lib1
            lib2 = "." + lib2
            lib3 = "." + lib3
        else:
            print "Could not locate C3 executable"
            return

        # Write C3 configuration file
        # c3cfg = tempfile.NamedTemporaryFile(
        # dir='.',prefix="c3_",suffix=".cfg",delete=False)
        c3cfg = filebasename + ".cfg"
        # print c3cfg
        # c3cfg = "./c3.txt"
        f = open(c3cfg, "w")
        f.write(c3inp + "\n")
        f.write(c3out + "\n")
        f.write(lib1 + "\n")
        f.write(lib2 + "\n")
        f.write("\n")
        f.write(lib3 + "\n")
        f.write(c3cax + "\n")
        newlines = '\n' * 7
        f.write(newlines)
        # c3cfg.close()
        f.close()
        # Tracer()()
        # Run C3 executable
        # cmd = "linrsh " + c3exe + " " + c3cfg
        # cmd = c3exe + " " + c3cfg
        print "Running c3 model"
        # args = ['linrsh', c3exe, c3cfg]
        arglist = ['linrsh', c3exe, c3cfg]
        arglist.insert(1, '-q')
        arglist.insert(2, 'all.q@wrath,all.q@envy,all.q@pride')
        #Tracer()()
        if grid:
            try:  # use linrsh if available
                call(arglist, shell=False)
            except:
                print "Warning: Grid is not available on the system."
                call(arglist[3:], shell=False)
        else:
            os.environ["TMPDIR"] = "/tmp"
            call(arglist[3:], shell=False)

        # Remove files
        # c3cfg.unlink(c3cfg.name)
        os.remove(c3cfg)
        # os.remove(c3inp)
        # c3out.unlink(c3out.name)
        # os.remove(c3out)

    def readc3cax(self, file_base_name, refcalc=False):

        # caxfile = "./c3.cax"
        caxfile = file_base_name + ".cax"
        if not os.path.isfile(caxfile):
            print "Could not open file " + caxfile
            return
        else:
            print "Reading file " + caxfile

        # Read the whole file at once
        with open(caxfile) as f:
            flines = f.read().splitlines()  # exclude \n

        # ------Search for regexp matches-------
        iTIT = self.__matchcontent(flines, '^TIT')
        iPOW = self.__matchcontent(flines, 'POW\s+')
        iPOL = self.__matchcontent(flines, '^POL')

        # Read fuel dimension
        npst = int(flines[iPOW[0]+1][4:6])

        # ------Step through the state points----------
        Nburnpts = len(iTIT)

        burnup = np.zeros(Nburnpts)
        burnup.fill(np.nan)
        voi = np.zeros(Nburnpts)
        voi.fill(np.nan)
        vhi = np.zeros(Nburnpts)
        vhi.fill(np.nan)
        tfu = np.zeros(Nburnpts)
        tfu.fill(np.nan)
        tmo = np.zeros(Nburnpts)
        tmo.fill(np.nan)
        kinf = np.zeros(Nburnpts)
        kinf.fill(np.nan)
        POW = np.zeros((npst, npst, Nburnpts))
        POW.fill(np.nan)

        # Row vector containing burnup, voi, vhi, tfu and tmo
        # rvec = [re.split('/',flines[i+2].strip()) for i in iTIT]
        rvec = [re.split('[/\s+]+', flines[i+2].strip()) for i in iTIT]

        # Row containing Kinf
        kinfstr = [flines[i+5] for i in iPOL]

        # Rows containing radial power distribution map
        powmap = [flines[i+2:i+2+npst] for i in iPOW]

        for i in xrange(Nburnpts):
            # Read burnup, voids, tfu and tmo
            burnup[i] = rvec[i][0]
            voi[i] = rvec[i][1]
            vhi[i] = rvec[i][2]
            tfu[i] = rvec[i][3]
            tmo[i] = rvec[i][4]
            # burnup[i],voi[i] = re.split('\s+',rvec[i][0].strip())
            # vhi[i],tfu[i] = re.split('\s+',rvec[i][1].strip())
            # tmo[i] = re.split('\s+',rvec[i][2].strip())[1]
            # Read kinf
            kinf[i] = re.split('\s+', kinfstr[i].strip())[0]
            # Read radial power distribution map
            POW[:, :, i] = self.__symtrans(self.__map2mat(powmap[i], npst))

        # Calculate radial burnup distributions
        EXP = self.__expcalc(POW, burnup)
        # Calculate Fint:
        fint = self.__fintcalc(POW)

        # Append state instancies
        statepoints = []

        # self.qcalc.append(DataStruct())
        # pindex = -1 # Index of last instance
        # self.qcalc[pindex].model = "c3"
        # self.qcalc[pindex].statepts = []
        for i in xrange(Nburnpts):
            # append new instance to list
            statepoints.append(DataStruct())
            statepoints[i].burnup = burnup[i]
            statepoints[i].voi = voi[i]
            statepoints[i].vhi = vhi[i]
            statepoints[i].tfu = tfu[i]
            statepoints[i].tmo = tmo[i]
            statepoints[i].kinf = kinf[i]
            statepoints[i].fint = fint[i]
            statepoints[i].POW = POW[:, :, i]
            statepoints[i].EXP = EXP[:, :, i]

        #if refcalc:
        #    self.states[0].refcalc = DataStruct()
        #    self.states[0].refcalc.statepoints = statepoints
        #else:
            # self.quickcalc_add(statepoints)
        self.statepoints = statepoints

    #def quickcalc_add(self, statepoints):
    #    """Adds the quickcalc differencies to the initial state"""
    #    sp0 = self.states[0].statepoints
    #    rsp = self.states[0].refcalc.statepoints
    #    sp1 = statepoints
    #
    #    N = len(sp1)
    #    # kinf
    #    dPOW = [sp1[i].POW - rsp[i].POW for i in range(N)]
    #    POW = np.array([dPOW[i] + sp0[i].POW for i in range(N)]).swapaxes(0, 2)
    #    fint = self.__fintcalc(POW)
    #    # burnup =
    #    # EXP = self.__expcalc(POW, burnup)
    #    # Tracer()()

    def quickcalc(self, voi=None, maxdep=60, depthres=None, refcalc=False,
                  grid=True, model='c3', box_offset=0.0, neulib=False):

        tic = time.time()
        # # LFU is set to original state only for testing purpose
        # LFU = self.states[0].LFU
        # FUE = self.states[0].FUE
        # # Append element to hold a new calculation
        # self.add_state(LFU, FUE, voi)
        # ---------------------------------

        file_base_name = "./tmp." + str(uuid.uuid4()).split('-')[0]
        self.writec3cai(file_base_name, voi, maxdep, depthres, box_offset)
        
        if model == 'c3':
            self.runc3(file_base_name, grid)
        elif model == 'c4':
            self.runc4(file_base_name, neulib, grid)
        else:
            print "Quickcalc model is unknown"
            return
        self.readc3cax(file_base_name, refcalc)
        self.ave_enr_calc()

        os.remove(file_base_name + ".inp")
        os.remove(file_base_name + ".out")
        os.remove(file_base_name + ".cax")
        try:
            os.remove(file_base_name + ".log")
        except:
            pass

        print "Done in "+str(time.time()-tic)+" seconds."

    def __boxbow(self, box_offset=0.0):
        """Updating the BWR card to account for box bowing."""
        bwr = self.data.bwr
        bwr_arr = bwr.split()
        
        gaw = float(bwr_arr[5]) + box_offset
        gan = float(bwr_arr[6]) - box_offset  # gaw + gan = constant
        bwr_arr[5] = str(gaw)
        bwr_arr[6] = str(gan)
        bwr_offset = ' '.join(bwr_arr)
        self.data.box_offset = box_offset
        return bwr_offset

    def __expcalc(self, POW, burnup):
        Nburnpts = burnup.size
        npst = POW.shape[0]
        EXP = np.zeros((npst, npst, Nburnpts))
        EXP.fill(np.nan)
        for i in range(Nburnpts):
            if burnup[i] == 0:
                EXP[:, :, i] = 0
            else:
                dburn = burnup[i] - burnup[i-1]
                if dburn < 0:
                    EXP[:, :, i] = POW[:, :, i]*burnup[i]
                else:
                    EXP[:, :, i] = EXP[:, :, i-1] + POW[:, :, i]*dburn
        return EXP

    def __fintcalc(self, POW):
        Nburnpts = POW.shape[2]
        fint = np.zeros(Nburnpts)
        fint.fill(np.nan)
        for i in range(Nburnpts):
            fint[i] = POW[:, :, i].max()
        return fint

    def findpoint(self, burnup=None, vhi=None, voi=None, tfu=None):
        """Return statepoint index that correspond to specific burnup,
        void and void history
        Syntax: pt = findpoint(burnup=burnup_val,vhi=vhi_val,voi=voi_val,
        tfu=tfu_val)"""
        statepoints = self.statepoints
        
        if tfu is not None:
            pindex = next(i for i, p in enumerate(statepoints) if p.tfu == tfu)
        elif burnup is not None:
            pindex = next(i for i, p in enumerate(statepoints)
                          if p.burnup == burnup and
                          p.vhi == vhi and p.voi == voi)
        else:
            pindex = next(i for i, p in enumerate(statepoints)
                          if p.vhi == vhi and p.voi == voi)
        return pindex

    def burnpoints(self, voi=40):
        """Return depletion vector for given voi (vhi=voi)"""
        
        statepoints = self.data.statepoints
        i = self.findpoint(voi=voi, vhi=voi)
        burnlist = [statepoints[i].burnup]
        Nstatepoints = len(statepoints)
        while ((i < Nstatepoints-1) and
               (statepoints[i].burnup <= statepoints[i+1].burnup)):
            burnlist.append(statepoints[i+1].burnup)
            i += 1
        return burnlist
    
    # def burnpoints(self, voi=40, stateindex=0):
    #    """Return depletion vector for given voi (vhi=voi)"""
    #    statepoints = self.states[stateindex].statepoints
    #    idx0 = self.findpoint(statepoints, voi=voi, vhi=voi)
    #    statepoints = statepoints[idx0:]
    #    Tracer()()
    #    burnup_old = 0.0
    #    for idx, p in enumerate(statepoints):
    #        print p.burnup
    #        if p.burnup <= burnup_old:
    #            break
    #        burnup_old = p.burnup
    #    Tracer()()
    #    burnlist = [statepoints[i].burnup for i in range(idx)]
    #    #Tracer()()
    #    return burnlist


if __name__ == '__main__':
    cas = casdata(sys.argv[1])
    cas.quickcalc()
