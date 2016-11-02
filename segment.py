#!/usr/bin/env python

# Run from ipython:
# > from casdata import casdata
# > case = casdata('caxfile')
#
# or:
# run casdata "caxfile"
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
from subprocess import call
import uuid  # used for random generated file names
'''
#from multiprocessing import Pool
#from btf import btf
#from pyqt_trace import pyqt_trace
'''


class DataStruct(object):
    """Initialize a class that can be used to structure data"""
    pass


class Segment(object):

    def __init__(self, caxfile=None, read_content=None):
        self.data = []
        self.add_calc()
        self.data[0].refcalc = DataStruct()
        '''
        #self.data.append(DataStruct()) # Add an element to list
        #self.data[-1]
        #self.statepts = []
        #self.pert = DataStruct()
        '''
        if caxfile:
            self.readcax(caxfile, read_content)
            self.ave_enr()
        '''
        #Tracer()()
        #self.qcalc = []
        #self.qcalc.append(DataStruct())

        #self.writecai()
        #self.btfcalc()
        '''

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

    def readcax(self, caxfile, read_content=None):

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
        if read_content != 'all':
            oTIT = self.__matchcontent(flines, '^TIT', 'object')
            while True:
                try:
                    i = oTIT.next()
                except:  # Reaching end of flines
                    break
                # split on spaces or '/'
                rstr = re.split('[/\s+]+', flines[i+2].strip())
                voi, vhi = rstr[1], rstr[2]
                # print voi,vhi,i
                if voi != vhi:
                    break
            flines = flines[:i]  # Reduce the number of lines in list
            # self.__flines = flines

        # Search for regexp matches
        print "Scanning file content..."
        '''
        # Loop through the whole file content
        #reglist = ['^TIT','^\s*FUE\s+']
        #self.__flines = flines
        #n = 2
        #p = Pool(n)
        #ilist = p.map(self.matchcontent, reglist)
        #p.close()
        #p.join()
        '''
        iTIT = self.__matchcontent(flines, '^TIT')
        iFUE = self.__matchcontent(flines, '^\s*FUE\s+')
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
            print "Could not find SLA card"
        iWRI = self.__matchcontent(flines, '^\s*WRI', 'next')
        iSTA = self.__matchcontent(flines, '^\s*STA', 'next')
        print "Done."
        # Read title
        # self.title = flines[iTTL[0]]
        self.data[-1].info.title = flines[iTTL[0]]
        # self.data.title = flines[iTTL[0]]
        # SIM
        # self.sim = flines[iSIM[0]]
        self.data[-1].info.sim = flines[iSIM[0]]
        # TFU
        # self.tfu = flines[iTFU]
        self.data[-1].info.tfu = flines[iTFU]
        # TMO
        # self.tmo = flines[iTMO]
        self.data[-1].info.tmo = flines[iTMO]
        # VOI
        # self.voi = flines[iVOI[0]]
        self.data[-1].info.voi = flines[iVOI[0]]
        # PDE
        # self.pde = flines[iPDE]
        self.data[-1].info.pde = flines[iPDE]
        # BWR
        # self.bwr = flines[iBWR]
        self.data[-1].info.bwr = flines[iBWR]
        # SPA
        # self.spa = flines[iSPA[0]]
        self.data[-1].info.spa = flines[iSPA[0]]
        # DEP
        # self.dep = flines[iDEP[0]]
        self.data[-1].info.dep = flines[iDEP[0]]
        # GAM
        # self.gam = flines[iGAM[0]]
        self.data[-1].info.gam = flines[iGAM[0]]
        # WRI
        # self.wri = flines[iWRI]
        self.data[-1].info.wri = flines[iWRI]
        # STA
        # self.sta = flines[iSTA]
        self.data[-1].info.sta = flines[iSTA]
        # CRD
        # self.crd = flines[iCRD[0]]
        self.data[-1].info.crd = flines[iCRD[0]]
        # Read fuel dimension
        npst = int(flines[iBWR][5:7])
        # Read LFU map
        caxmap = flines[iLFU+1:iLFU+1+npst]
        LFU = self.__symtrans(self.__map2mat(caxmap, npst)).astype(int)

        # Read LPI map
        caxmap = flines[iLPI+1:iLPI+1+npst]
        LPI = self.__symtrans(self.__map2mat(caxmap, npst)).astype(int)

        # Read FUE
        # iFUE = iFUE[iFUE<iEND[0]]
        iFUE = [i for i in iFUE if i < iEND]
        # iFUE = filter(lambda x,y=iEND:x<y,iFUE)
        # Nfue = iFUE.size
        Nfue = len(iFUE)
        FUE = np.zeros((Nfue, 5))
        FUE.fill(np.nan)
        for i, idx in enumerate(iFUE):
            rvec = re.split('\*', flines[idx].strip())
            rstr = rvec[0]
            rvec = re.split('\s+', rstr.strip())
            FUE[i, 0] = rvec[1]
            FUE[i, 1:3] = re.split('/', rvec[2])
            if np.size(rvec) > 3:
                FUE[i, 3:5] = re.split('=', rvec[3])

        # Translate LFU map to ENR map
        ENR = np.zeros((npst, npst))
        for i in range(Nfue):
            ifu = int(FUE[i, 0])
            ENR[LFU == ifu] = FUE[i, 2]

        # Translate LFU map to BA map
        BA = np.zeros((npst, npst))
        for i in range(Nfue):
            ifu = int(FUE[i, 0])
            if np.isnan(FUE[i, 3]):
                BA[LFU == ifu] = 0.0
            else:
                BA[LFU == ifu] = FUE[i, 4]

        # Determine number of BA rods types
        Nba = 0
        for content in FUE[:, 4]:
            if not np.isnan(content):
                Nba += 1

        # Read PIN (pin radius)
        # Npin = iPIN.size
        Npin = len(iPIN)
        ncol = 4
        PIN = np.zeros((Npin, ncol))
        PIN.fill(np.nan)
        for i, idx in enumerate(iPIN):
            rvec = re.split(',|/', flines[idx].strip())
            rstr = rvec[0]
            rvec = re.split('\s+', rstr.strip())
            rlen = np.size(rvec)
            PIN[i, :rlen-1] = rvec[1:ncol+1]

        # self.pinlines = flines[iPIN[0]:iPIN[0]+Npin]
        self.data[-1].info.pinlines = flines[iPIN[0]:iPIN[0]+Npin]

        # Read SLA
        if iSLA is not None:
            self.data[-1].info.slaline = flines[iSLA]
        # ------Step through the state points----------
        print "Stepping through state points..."

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
        rvec = [re.split('[/\s+]+', flines[i+2].strip()) for i in iTIT]

        # Row containing Kinf
        kinfstr = [flines[i+5] for i in iPOL]

        # Rows containing radial power distribution map
        powmap = [flines[i+2:i+2+npst] for i in iPOW]

        # Rows containing XFL maps
        xfl1map = [flines[i+2:i+2+npst] for i in iXFL]
        xfl2map = [flines[i+3+npst:i+3+2*npst] for i in iXFL]

        for i in range(Nburnpts):
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
            # Read XFL maps
            XFL1[:, :, i] = self.__symtrans(self.__map2mat(xfl1map[i], npst))
            XFL2[:, :, i] = self.__symtrans(self.__map2mat(xfl2map[i], npst))
        print "Done."
        # --------------------------------------------------------------------
        # Calculate radial burnup distributions
        EXP = self.__expcalc(POW, burnup)
        # Calculate Fint:
        fint = self.__fintcalc(POW)

        # Append state instancies
        for i in range(Nburnpts):
            # append new instance to list
            self.data[-1].statepoints.append(DataStruct())
            # state = data()
            self.data[-1].statepoints[i].titcrd = titcrd[i]
            self.data[-1].statepoints[i].burnup = burnup[i]
            # state.burnup = burnup[i]
            self.data[-1].statepoints[i].voi = voi[i]
            # state.voi = voi[i]
            self.data[-1].statepoints[i].vhi = vhi[i]
            # state.vhi = vhi[i]
            self.data[-1].statepoints[i].tfu = tfu[i]
            # state.tfu = tfu[i]
            self.data[-1].statepoints[i].tmo = tmo[i]
            # state.tmo = tmo[i]
            self.data[-1].statepoints[i].kinf = kinf[i]
            # state.kinf = kinf[i]
            self.data[-1].statepoints[i].fint = fint[i]
            # state.fint = fint[i]
            self.data[-1].statepoints[i].EXP = EXP[:, :, i]
            # state.EXP = EXP[:,:,i]
            self.data[-1].statepoints[i].XFL1 = XFL1[:, :, i]
            # state.XFL1 = XFL1[:,:,i]
            self.data[-1].statepoints[i].XFL2 = XFL2[:, :, i]
            # state.XFL2 = XFL2[:,:,i]
            self.data[-1].statepoints[i].POW = POW[:, :, i]
            # state.POW = POW[:,:,i]
            # self.data["statepts"].append(state)

        # Saving geninfo
        # self.geninfo = data()
        self.data[-1].info.caxfile = caxfile
        # info.caxfile = caxfile
        self.data[-1].info.ENR = ENR
        # info.ENR = ENR
        self.data[-1].info.BA = BA
        # info.BA = BA
        self.data[-1].info.PIN = PIN
        # info.PIN = PIN
        self.data[-1].info.LPI = LPI
        # info.LPI = LPI
        self.data[-1].info.FUE = FUE
        # info.FUE = FUE
        self.data[-1].info.LFU = LFU
        # info.LFU = LFU
        self.data[-1].info.npst = npst
        # info.npst = npst
        # self.data['geninfo'] = info
        '''
        #self.caxfile = caxfile
        #self.burnvec = burnup
        #self.voivec = voi
        #self.vhivec = vhi
        #self.tfuvec = tfu
        #self.tmovec = tmo
        #self.kinf = kinf
        #self.fint = fint
        #self.EXP = EXP
        #self.ENR = ENR
        #self.BA = BA
        #self.PIN = PIN
        #self.LPI = LPI
        #self.FUE = FUE
        #self.LFU = LFU
        #self.npst = npst
        #self.POW = POW
        #self.XFL1 = XFL1
        #self.XFL2 = XFL2
        '''

#    def btfcalc(self):
#        btf('SVEA-96','')

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

#    #---------Calculate Fint-------------
#    def fint(self):
#        Nburnpts = self.POW.shape[2]
#        fint = np.zeros(Nburnpts); fint.fill(np.nan)
#        for i in range(Nburnpts):
#            fint[i] = self.POW[:,:,i].max()
#        self.fint = fint

    # --------Calculate average enrichment----------
    def ave_enr(self):

        # Translate LFU map to density map
        data = self.data[-1].info
        npst = data.npst
        DENS = np.zeros((npst, npst))
        Nfue = data.FUE[:, 0].size
        for i in range(Nfue):
            ifu = int(data.FUE[i, 0])
            DENS[data.LFU == ifu] = data.FUE[i, 1]

        # Translate LPI map to pin radius map
        RADI = np.zeros((npst, npst))
        Npin = data.PIN[:, 0].size
        for i in range(Npin):
            ipi = int(data.PIN[i, 0])
            RADI[data.LPI == ipi] = data.PIN[i, 1]

        # Calculate mass
        VOLU = np.pi*RADI**2
        MASS = DENS*VOLU
        mass = np.sum(MASS)
        ENR = data.ENR
        MASS_U235 = MASS*ENR
        mass_u235 = np.sum(MASS_U235)
        self.data[-1].info.ave_enr = mass_u235/mass

    # -------Write cai file------------
    def writecai(self, caifile):
        print "Writing to file " + caifile

        f = open(caifile, 'w')
        f.write(self.data.title + '\n')
        f.write(self.data.sim + '\n')
        f.write(self.data.tfu + '\n')
        f.write(self.data.tmo + '\n')
        f.write(self.data.voi + '\n')

        Nfue = self.data.FUE.shape[0]
        for i in range(Nfue):
            f.write(' FUE  %d ' % (self.data.FUE[i, 0]))
            f.write('%5.3f/%5.3f' % (self.data.FUE[i, 1], self.data.FUE[i, 2]))
            if ~np.isnan(self.data.FUE[i, 3]):
                f.write(' %d=%4.2f' % (self.data.FUE[i, 3],
                                       self.data.FUE[i, 4]))
            f.write('\n')

        f.write(' LFU\n')
        for i in range(self.data.npst):
            for j in range(i+1):
                f.write(' %d' % self.data.LFU[i, j])
                # if j < i: f.write(' ')
            f.write('\n')

        f.write(self.data.pde + '\n')

        f.write(self.data.bwr + '\n')

        Npin = np.size(self.data.pinlines)
        for i in range(Npin):
            f.write(self.data.pinlines[i] + '\n')

        f.write(self.data.slaline.strip() + '\n')

        f.write(' LPI\n')
        for i in range(self.data.npst):
            for j in range(i+1):
                f.write(' %d' % self.data.LPI[i, j])
                # if j < i: f.write(' ')
            f.write('\n')

        f.write(self.data.spa + '\n')
        f.write(self.data.dep + '\n')
        f.write(self.data.gam + '\n')
        f.write(self.data.wri + '\n')
        f.write(self.data.sta + '\n')

        f.write(' TTL\n')

        depstr = re.split('DEP', self.data.dep)[1].replace(',', '').strip()
        f.write(' RES,,%s\n' % (depstr))

        # f.write(' RES,,0 0.5 1.5 2.5 5.0 7.5 10.0 12.5 15.0 17.5 20.0 25
        # 30 40 50 60 70\n')
        f.write(self.data.crd + '\n')
        f.write(' NLI\n')
        f.write(' STA\n')
        f.write(' END\n')

        f.close()

    def add_calc(self):
        """Append a list element to store result of new calculation"""
        self.data.append(DataStruct())  # Add an element to list
        self.data[-1].info = DataStruct()
        self.data[-1].statepoints = []

    def writec3cai(self, file_base_name, voi=None, maxdep=None,
                   box_offset=False):
        # filebasename = "./" + str(uuid.uuid4())
        c3inp = file_base_name + ".inp"
        # c3inp = tempfile.NamedTemporaryFile(dir='.',
        # prefix="c3_",suffix=".inp",delete=False)
        print "Writing c3 input file " + c3inp

        # info = self.data[0]['info']  # Get info data from original import
        info = self.data[0].info
        if hasattr(self.data[-1].info, 'LFU'):
            LFU = self.data[-1].info.LFU  # Get LFU from last calc
        else:
            print "Error: LFU is missing."
            return

        # info = self.db['origin']['info']
        # LFU = self.db['qcalc'][-1]['info'].get('LFU')

        # f = c3inp.file
        f = open(c3inp, 'w')

        tit_1 = "TIT "
        tit_2 = info.tfu.split('*')[0].replace(',', '=').strip() + " "
        tit_3 = info.tmo.split('*')[0].replace(',', '=').strip() + " "
        tit = tit_1 + tit_2 + tit_3
        if voi is None:
            voivec = info.voi.split('*')[0].replace(',', ' ')\
                                                  .strip().split(' ')[1:]
            tit = tit + "VOI=" + voivec[0] + " "
            ide = ["'BD"+x+"'" for x in voivec]
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
            for j in range(i+1):
                f.write('%d ' % LFU[i, j])
            f.write('\n')

        pde = info.pde.split('\'')[0]
        f.write(pde.strip() + '\n')
        if box_offset:
            bwr = self.boxbow(box_offset)
            f.write(bwr + '\n')
        else:
            f.write(info.bwr.strip() + '\n')

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

        if hasattr(info,'slaline'):  # has water cross?
            if info.slaline:  # check that it is not empty
                f.write(info.slaline.strip() + '\n')

        f.write('LPI\n')
        for i in xrange(info.npst):
            for j in xrange(i+1):
                f.write('%d ' % info.LPI[i, j])
            f.write('\n')

        f.write(info.spa.strip() + '\n')
        if maxdep is None:
            f.write(info.dep.strip() + '\n')
        else:
            depstr = "DEP 0, 0.001, -" + str(maxdep)
            f.write(depstr + '\n')

        f.write('NLI\n')
        f.write('STA\n')

        if voi is None:
            N = len(ide)
            for i in xrange(1, N):
                f.write(tit + "IDE=" + ide[i] + '\n')
                res = "RES," + ide[i-1] + ",0"
                f.write(res + '\n')
                f.write("VOI " + voivec[i] + '\n')
                if maxdep is None:
                    f.write(info.dep.strip() + '\n')
                else:
                    depstr = "DEP 0, 0.001, -" + str(maxdep)
                    f.write(depstr + '\n')

                f.write('STA\n')

        f.write('END\n')
        # c3inp.close()
        f.close()
        # return filebasename

    def runc3(self, filebasename, grid=False):  # Running C3 perturbation model
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
        print c3cfg
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
        print "running c3 model"
        if grid:
            try:  # use linrsh if available
                call(['linrsh', c3exe, c3cfg])
            except:
                pass
        else:
            call([c3exe, c3cfg])

        # Remove files
        # c3cfg.unlink(c3cfg.name)
        os.remove(c3cfg)
        # os.remove(c3inp)
        # c3out.unlink(c3out.name)
        # os.remove(c3out)

    def readc3cax(self, file_base_name, opt=None):

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

        for i in range(Nburnpts):
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
        for i in range(Nburnpts):
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

            '''
            self.qcalc[pindex].statepts.append(DataStruct())
            self.qcalc[pindex].statepts[i].burnup = burnup[i]
            self.qcalc[pindex].statepts[i].voi = voi[i]
            self.qcalc[pindex].statepts[i].vhi = vhi[i]
            self.qcalc[pindex].statepts[i].tfu = tfu[i]
            self.qcalc[pindex].statepts[i].tmo = tmo[i]
            self.qcalc[pindex].statepts[i].kinf = kinf[i]
            self.qcalc[pindex].statepts[i].fint = fint[i]
            self.qcalc[pindex].statepts[i].POW = POW[:,:,i]
            self.qcalc[pindex].statepts[i].EXP = EXP[:,:,i]
            '''
        if opt == 'refcalc':
            self.data[0].refcalc.statepoints = statepoints
        else:
            self.data[-1].statepoints = statepoints

        # os.remove(caxfile)

    def quickcalc(self, voi=None, maxdep=None, opt='refcalc', grid=False):
        tic = time.time()
        # if opt != 'refcalc':
        #    self.add_calc()  # Append element to hold a new calculation
        # self.data[-1].info.LFU = self.data[0].info.LFU
        file_base_name = "./" + str(uuid.uuid4())
        self.writec3cai(file_base_name, voi, maxdep, box_offset=False)
        self.runc3(file_base_name, grid)
        self.readc3cax(file_base_name, opt)
        os.remove(file_base_name + ".inp")
        os.remove(file_base_name + ".out")
        os.remove(file_base_name + ".cax")
        print "Done in "+str(time.time()-tic)+" seconds."

    '''
    def quickcalc(self,model='c3'):
        tic = time.time()
        if model == 'c3':
            voi = 50
            maxburn = 60
            print "Running perturbation model for void "+str(voi)
            self.writec3cai_singlevoi(voi,maxburn)
            self.runc3()
            self.readc3cax()
        print "Done in "+str(time.time()-tic)+" seconds."
    '''

    def boxbow(self, box_offset=0.0):
        """Updating the BWR card to account for box bowing."""
        bwr = self.data[-1].info.bwr
        bwr_arr = bwr.split()
        gaw = float(bwr_arr[5]) + box_offset
        gan = float(bwr_arr[6]) - box_offset  # gaw + gan = constant
        bwr_arr[5] = str(gaw)
        bwr_arr[6] = str(gan)
        bwr_offset = ' '.join(bwr_arr)
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

    def findpoint(self, statepoints,
                  burnup=None, vhi=None, voi=None, tfu=None):
        """Return statepoint index that correspond to specific burnup,
        void and void history
        Syntax: pt = findpoint(burnup=burnup_val,vhi=vhi_val,voi=voi_val,
        tfu=tfu_val)"""

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

    def burnpoints(self, voi=None, vhi=None, calcindex=0):
        """Return depletion vector for given voi"""

        statepoints = self.data[calcindex].statepoints
        i = self.findpoint(statepoints, voi=voi, vhi=vhi)
        burnlist = [statepoints[i].burnup]
        Nstatepoints = len(statepoints)
        while ((i < Nstatepoints-1) and
               (statepoints[i].burnup <= statepoints[i+1].burnup)):
            burnlist.append(statepoints[i+1].burnup)
            i += 1
        return burnlist

if __name__ == '__main__':
    cas = casdata(sys.argv[1])
    cas.quickcalc()
