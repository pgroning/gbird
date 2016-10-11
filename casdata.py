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
#import os.path
import sys
import time
from subprocess import call
import uuid # used for random generated file names
#import tempfile
#from multiprocessing import Pool
#from btf import btf
#from pyqt_trace import pyqt_trace


#class datastruct(object):
#    """Initialize a class that can be used to structure data"""
#    pass


class casdata(object):
    """class that manage camso input and output data.
    If opt is different from 'all' only statepoints for main voids will
    be imported. If not defined all statepoints will be read."""

    def __init__(self,caxfile=None,opt='all'):
        
        # Initialize a 'data' attribute as a list in order to organize data.
        # Each element in list is supposed to contain the result of a particular calculation.
        # The first index (0) contains the imported base data and subsequent indices holds the
        # results from quick calcs.
        self.data = []
        self.add_calc() # Add an element to list
        self.data[0].update(refcalc={}) # Add 'refcalc' dictionary

        if caxfile is not None:
            # Import data from original cax file and store the result in self.data[0]
            #self.add_calc() # Add an element to list
            self.readcax(caxfile,opt)

            # Calculate average enrichment for the segment
            self.ave_enr()
            
            # Perform quick calc reference calculation
            #self.data[0].update(refcalc={})
            filebasename = self.writec3cai() # Create c3 input file and return the file name
            self.runc3(filebasename) # run the c3 model
            self.readc3cax(filebasename,'refcalc') # import the result and store the data under 'refcalc' field
        

        '''
        # Initialize a 'db' attribute as a dictionary in order to hold data
        self.db = dict()
        self.db.update(origin={})
        self.db['origin'] = {'info':{}, 'statepoints':[]}
        self.db.update(qcalc={})
        #self.db['qcalc'] = {'info':{}, 'statepoints':[]}
        self.db['qcalc'] = []
        self.add_qcalc()
        #self.db['qcalc'].append({'info':{}, 'statepoints':[]})
        
        self.readcax(caxfile,opt)
        self.__ave_enr()

        self.writec3cai()
        self.runc3()
        self.readc3cax()
        #self.qcalc = []
        #self.qcalc.append(datastruct())
        '''
        #self.writecai()
        #self.btfcalc()


    # -------Read cax file---------
    def __matchcontent(self,regexp,opt='all'):
        rec = re.compile(regexp)
        if opt == 'all':
            out = [i for i,x in enumerate(self.__flines) if rec.match(x)]
        elif opt == 'next':
            out = next(i for i,x in enumerate(self.__flines) if rec.match(x))
        elif opt == 'object':
            out = (i for i,x in enumerate(self.__flines) if rec.match(x))
        return out

    def readcax(self,caxfile,opt): # Read the from original cax file
        
        if not os.path.isfile(caxfile):
            print "Could not open file " + caxfile
            return
        else:
            print "Reading file " + caxfile
                
        # Read input file up to maxlen using random access
        #maxlen = 100000
        #flines = []
        #for i in range(maxlen):
        #    flines.append(linecache.getline(caxfile,i+1).rstrip())

        # Read the whole file
        with open(caxfile) as f:
           #flines = f.readlines() # include \n
            flines = f.read().splitlines() #exclude \n

        # Search for regexp matches
        self.__flines = flines
        if opt != 'all': # Find last index containing voids voi=vhi
            oTIT = self.__matchcontent('^TIT','object')
            while True:
                try:
                    i = oTIT.next()
                except: # Reaching end of flines
                    break
                # split on spaces or '/'
                rstr = re.split('[/\s+]+',flines[i+2].strip())
                voi,vhi = rstr[1],rstr[2]
                #print voi,vhi,i
                if voi != vhi: break
            flines = flines[:i] # Reduce the number of lines in list
            self.__flines = flines
        
        print "Scanning file content..."
        
        # Loop through the whole file content
        #reglist = ['^TIT','^\s*FUE\s+']
        #self.__flines = flines
        #n = 2
        #p = Pool(n)
        #ilist = p.map(self.matchcontent, reglist)
        #p.close()
        #p.join()
        iTIT = self.__matchcontent('^TIT')
        iFUE = self.__matchcontent('^\s*FUE\s+')
        iPOW = self.__matchcontent('POW\s+')
        iSIM = self.__matchcontent('^\s*SIM')
        iSPA = self.__matchcontent('^\s*SPA')
        iGAM = self.__matchcontent('^\s*GAM')
        iCRD = self.__matchcontent('^\s*CRD')
        iPOL = self.__matchcontent('^POL')
        iXFL = self.__matchcontent('^XFL')
        iPIN = self.__matchcontent('^\s*PIN')
        iTTL = self.__matchcontent('^\s*TTL')
        iVOI = self.__matchcontent('^\s*VOI')
        iDEP = self.__matchcontent('^\s*DEP')
        
        # Stop looping at first match
        iEND = self.__matchcontent('^\s*END','next')
        iBWR = self.__matchcontent('^\s*BWR','next')
        iLFU = self.__matchcontent('^\s*LFU','next')
        iLPI = self.__matchcontent('^\s*LPI','next')
        iTFU = self.__matchcontent('^\s*TFU','next')
        iTMO = self.__matchcontent('^\s*TMO','next')
        iPDE = self.__matchcontent('^\s*PDE','next')
        try: # Card for water cross (valid for OPT2/3)
            iSLA = self.__matchcontent('^\s*SLA','next')
        except: iSLA = None
        iWRI = self.__matchcontent('^\s*WRI','next')
        iSTA = self.__matchcontent('^\s*STA','next')
        print "Done."

        # Sort data
        data = dict()

        # Read title
        data['title'] = flines[iTTL[0]]
        # SIM
        data['sim'] = flines[iSIM[0]]
        # TFU
        data['tfu'] = flines[iTFU]
        # TMO
        data['tmo'] = flines[iTMO]
        # VOI
        data['voi'] = flines[iVOI[0]]
        # PDE
        data['pde'] = flines[iPDE]
        # BWR
        data['bwr'] = flines[iBWR]
        # SPA
        data['spa'] = flines[iSPA[0]]
        # DEP
        data['dep'] = flines[iDEP[0]]
        # GAM
        data['gam'] = flines[iGAM[0]]
        # WRI
        data['wri'] = flines[iWRI]
        # STA
        data['sta'] = flines[iSTA]
        # CRD
        data['crd'] = flines[iCRD[0]]

        # Read fuel dimension
        npst = int(flines[iBWR][5:7])
        
        # Read LFU map
        caxmap = flines[iLFU+1:iLFU+1+npst]
        LFU = self.__symtrans(self.__map2mat(caxmap,npst)).astype(int)

        # Read LPI map
        caxmap = flines[iLPI+1:iLPI+1+npst]
        LPI = self.__symtrans(self.__map2mat(caxmap,npst)).astype(int)
        
        # Read FUE
        #iFUE = iFUE[iFUE<iEND[0]]
        #Tracer()()
        iFUE = [i for i in iFUE if i<iEND]
        #iFUE = filter(lambda x, y=iEND: x < y, iFUE)
        #Nfue = iFUE.size
        Nfue = len(iFUE)
        FUE = np.zeros((Nfue,5)); FUE.fill(np.nan)
        for i,idx in enumerate(iFUE):
            rvec = re.split('\*',flines[idx].strip())
            rstr = rvec[0]
            rvec = re.split('\s+',rstr.strip())
            FUE[i,0] = rvec[1]
            FUE[i,1:3] = re.split('/',rvec[2])
            if np.size(rvec) > 3:
                FUE[i,3:5] = re.split('=',rvec[3])
        
        # Translate LFU map to ENR map
        ENR = np.zeros((npst,npst)); #ENR.fill(np.nan)
        for i in range(Nfue):
            ifu = int(FUE[i,0])
            ENR[LFU==ifu] = FUE[i,2]

        # Translate LFU map to BA map
        BA = np.zeros((npst,npst)); #BA.fill(np.nan)
        for i in range(Nfue):
            ifu = int(FUE[i,0])
            if np.isnan(FUE[i,3]):
                BA[LFU==ifu] = 0.0
            else:
                BA[LFU==ifu] = FUE[i,4]
        
        # Determine number of BA rods types
        Nba = 0
        for content in FUE[:,4]:
            if np.isnan(content) == False:
                Nba += 1
                
        # Read PIN (pin radius)
        Npin = len(iPIN)
        ncol = 4
        PIN = np.zeros((Npin,ncol)); PIN.fill(np.nan)
        for i,idx in enumerate(iPIN):
            rvec = re.split(',|/',flines[idx].strip())
            rstr = rvec[0]
            rvec = re.split('\s+',rstr.strip())
            rlen = np.size(rvec)
            PIN[i,:rlen-1] = rvec[1:ncol+1]

        data['pinlines'] = flines[iPIN[0]:iPIN[0]+Npin]
        
        # Read SLA
        if iSLA is not None:
            data['slaline'] = flines[iSLA]

        # Append to data to the last list element
        self.data[-1]['info'].update(data)

        #---OLD---
        # Append data to db dictionary
        #self.db['origin']['info'].update(data)
        #---OLD---

        # ------Step through the state points----------
        print "Stepping through state points..."
        
        Nburnpoints = len(iTIT)

        # Read title cards
        titcrd = [flines[i] for i in iTIT]

        # Row vector containing burnup, voi, vhi, tfu and tmo
        rvec = [re.split('[/\s+]+',flines[i+2].strip()) for i in iTIT]
        burnup = np.array([rvec[i][0] for i in xrange(Nburnpoints)]).astype(float)
        voi = np.array([rvec[i][1] for i in xrange(Nburnpoints)]).astype(float)
        vhi = np.array([rvec[i][2] for i in xrange(Nburnpoints)]).astype(float)
        tfu = np.array([rvec[i][3] for i in xrange(Nburnpoints)]).astype(float)
        tmo = np.array([rvec[i][5] for i in xrange(Nburnpoints)]).astype(float)

        # Row containing Kinf
        kinfstr = [flines[i+5] for i in iPOL]
        kinf = np.array([re.split('\s+',kinfstr[i].strip())[0] for i in xrange(Nburnpoints)]).astype(float)

        # Rows containing radial power distribution map
        powmap = [flines[i+2:i+2+npst] for i in iPOW]
        POW = np.array([self.__symtrans(self.__map2mat(powmap[i],npst)) for i in xrange(Nburnpoints)]).swapaxes(0,2)

        # Rows containing XFL maps
        xfl1map = [flines[i+2:i+2+npst] for i in iXFL]
        XFL1 = np.array([self.__symtrans(self.__map2mat(xfl1map[i],npst)) for i in xrange(Nburnpoints)]).swapaxes(0,2)

        xfl2map = [flines[i+3+npst:i+3+2*npst] for i in iXFL]
        XFL2 = np.array([self.__symtrans(self.__map2mat(xfl2map[i],npst)) for i in xrange(Nburnpoints)]).swapaxes(0,2)

        #for i in xrange(Nburnpoints):
            # Read radial power distribution map
            #POW[:,:,i] = self.__symtrans(self.__map2mat(powmap[i],npst))
            # Read XFL maps
            #XFL1[:,:,i] = self.__symtrans(self.__map2mat(xfl1map[i],npst))
            #XFL2[:,:,i] = self.__symtrans(self.__map2mat(xfl2map[i],npst))
 
        # -----------------------------------------------------------------------
        # Calculate radial burnup distributions
        EXP = self.__expcalc(POW,burnup)
        # Calculate Fint:
        fint = self.__fintcalc(POW)

        # Append state instancies
        statepoints = [{'titcrd':titcrd[i],'burnup':burnup[i],'voi':voi[i],'vhi':vhi[i],'tfu':tfu[i],\
                            'tmo':tmo[i],'kinf':kinf[i],'fint':fint[i],'EXP':EXP[:,:,i],'XFL1':XFL1[:,:,i],\
                            'XFL2':XFL2[:,:,i],'POW':POW[:,:,i]} for i in xrange(Nburnpoints)]
        '''
        statepoints = []
        for i in xrange(Nburnpoints):
            statepoints.append({}) # append new dictionary to list
            statepoints[i]['titcrd'] = titcrd[i]
            statepoints[i]['burnup'] = burnup[i]
            statepoints[i]['voi'] = voi[i]
            statepoints[i]['vhi'] = vhi[i]
            statepoints[i]['tfu'] = tfu[i]
            statepoints[i]['tmo'] = tmo[i]
            statepoints[i]['kinf'] = kinf[i]
            statepoints[i]['fint'] = fint[i]
            statepoints[i]['EXP'] = EXP[:,:,i]
            statepoints[i]['XFL1'] = XFL1[:,:,i]
            statepoints[i]['XFL2'] = XFL2[:,:,i]
            statepoints[i]['POW'] = POW[:,:,i]
        '''
        # Append statepoints to last element
        self.data[-1]['statepoints'] = statepoints

        #---OLD---
        # Append statepoints to db
        #self.db['origin']['statepoints'] = statepoints
        #---OLD---

        # Saving geninfo
        geninfo = dict()
        geninfo['caxfile'] = caxfile
        geninfo['ENR'] = ENR
        geninfo['BA'] = BA
        geninfo['PIN'] = PIN
        geninfo['LPI'] = LPI
        geninfo['FUE'] = FUE
        geninfo['LFU'] = LFU
        geninfo['npst'] = npst

        # Append geninfo to data attribute
        self.data[-1]['info'].update(geninfo)


        #---OLD----
        # Append geninfo to db
        #self.db['origin']['info'].update(geninfo)
        # also append LFU to 'qcalc'
        #self.db['qcalc'][-1]['info']['LFU'] = LFU
        #----OLD----

#    def btfcalc(self):
#        btf('SVEA-96','')
        
        
    def __map2mat(self,caxmap,dim):
        M = np.zeros((dim,dim)); M.fill(np.nan)
        for i in range(dim):
            rstr = caxmap[i]
            rvec = re.split('\s+',rstr.strip())
            M[i,0:i+1] = rvec
        return M

    def __symtrans(self,M):
        Mt = M.transpose()
        dim = M.shape[0]
        for i in range(1,dim):
            Mt[i,0:i] = M[i,0:i]
        return Mt


#    #---------Calculate Fint-------------
#    def fint(self):
#        Nburnpoints = self.POW.shape[2]
#        fint = np.zeros(Nburnpoints); fint.fill(np.nan)
#        for i in range(Nburnpoints):
#            fint[i] = self.POW[:,:,i].max()
#        self.fint = fint

    # --------Calculate average enrichment----------
    def ave_enr(self):
        #Tracer()()
        data = self.data[-1]['info'];
        #data = self.db['origin']['info']

        # Translate LFU map to density map
        npst = data.get('npst')
        DENS = np.zeros((npst,npst))
        FUE = data.get('FUE')
        LFU = data.get('LFU')
        Nfue = FUE[:,0].size
        
        for i in xrange(Nfue):
            ifu = int(FUE[i,0])
            DENS[LFU==ifu] = FUE[i,1]
        
        # Translate LPI map to pin radius map
        RADI = np.zeros((npst,npst))
        PIN = data.get('PIN')
        LPI = data.get('LPI')
        Npin = PIN[:,0].size
        for i in range(Npin):
            ipi = int(PIN[i,0])
            RADI[LPI==ipi] = PIN[i,1]
        
        # Calculate mass
        VOLU = np.pi*RADI**2
        MASS = DENS*VOLU
        mass = np.sum(MASS)
        ENR = data.get('ENR')
        MASS_U235 = MASS*ENR
        mass_u235 = np.sum(MASS_U235)
        ave_enr = mass_u235/mass
        
        # Append the result to data
        self.data[-1]['info']['ave_enr'] = ave_enr

        #---OLD---
        #self.db['origin']['info']['ave_enr'] = ave_enr
        #---OLD---

    # -------Write cai file------------
    def writecai(self,caifile):
        print "Writing to file " + caifile
        
        #caifile = "cas.inp"

        f = open(caifile,'w')
        f.write(self.data.title + '\n')
        f.write(self.data.sim + '\n')
        f.write(self.data.tfu + '\n')
        f.write(self.data.tmo + '\n')
        f.write(self.data.voi + '\n')

        Nfue = self.data.FUE.shape[0]
        for i in range(Nfue):
            f.write(' FUE  %d ' % (self.data.FUE[i,0]))
            f.write('%5.3f/%5.3f' % (self.data.FUE[i,1],self.data.FUE[i,2]))
            if ~np.isnan(self.data.FUE[i,3]):
                f.write(' %d=%4.2f' % (self.data.FUE[i,3],self.data.FUE[i,4]))
            f.write('\n')

        f.write(' LFU\n')
        for i in range(self.data.npst):
            for j in range(i+1):
                f.write(' %d' % self.data.LFU[i,j])
                #if j < i: f.write(' ')
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
                f.write(' %d' % self.data.LPI[i,j])
                #if j < i: f.write(' ')
            f.write('\n')

        f.write(self.data.spa + '\n')
        f.write(self.data.dep + '\n')
        f.write(self.data.gam + '\n')
        f.write(self.data.wri + '\n')
        f.write(self.data.sta + '\n')

        f.write(' TTL\n')

        depstr = re.split('DEP',self.data.dep)[1].replace(',','').strip()
        f.write(' RES,,%s\n' % (depstr))

        #f.write(' RES,,0 0.5 1.5 2.5 5.0 7.5 10.0 12.5 15.0 17.5 20.0 25 30 40 50 60 70\n')
        f.write(self.data.crd + '\n')
        f.write(' NLI\n')
        f.write(' STA\n')
        f.write(' END\n')

        f.close()

        #Tracer()()

    def writec3cai_singlevoi(self,voi=40,maxdep=60):
        c3inp = "./c3.inp"
        print "Writing c3 input file " + c3inp

        if hasattr(self.qcalc[-1],'LFU'):
            LFU = self.qcalc[-1].LFU
        else:
            LFU = self.data.LFU
        
        #LFU = self.qcalc[-1].LFU
        #LFU = self.data.LFU
        #FUE = self.qcalc[-1].FUE
        #pyqt_trace()

        f = open(c3inp,'w')
        tit = "TIT "
        tit = tit + self.data.tfu.split('*')[0].replace(',','=').strip() + " "
        tit = tit + self.data.tmo.split('*')[0].replace(',','=').strip() + " "
        tit = tit + "VOI=" + str(voi) + " "
        f.write(tit + '\n')
        f.write(self.data.sim.strip() + '\n')

        Nfue = self.data.FUE.shape[0]
        for i in range(Nfue):
            f.write('FUE  %d ' % (self.data.FUE[i,0]))
            f.write('%5.3f/%5.3f' % (self.data.FUE[i,1],self.data.FUE[i,2]))
            if ~np.isnan(self.data.FUE[i,3]):
                f.write(' %d=%4.2f' % (self.data.FUE[i,3],self.data.FUE[i,4]))
            f.write('\n')
        
        f.write('LFU\n')
        for i in range(self.data.npst):
            for j in range(i+1):
                f.write('%d ' % LFU[i,j])
                #f.write('%d ' % self.data.LFU[i,j])
            f.write('\n')

        pde = self.data.pde.split('\'')[0]
        f.write(pde.strip() + '\n')
        f.write(self.data.bwr.strip() + '\n')

        Npin = np.size(self.data.pinlines)
        for i in range(Npin):
            tmpstr = re.split('\*|/',self.data.pinlines[i].strip())[0]# Remove coments etc
            pinarr = re.split(',|\s+',tmpstr.strip()) # Split for segments
            npinsegs = len(pinarr)-2
            if npinsegs > 3:
                red_pinstr = ' '.join(pinarr[0:3]+pinarr[-2:])
            else:
                red_pinstr = self.data.pinlines[i].strip()
            f.write(red_pinstr.strip() + '\n')
            #f.write(self.data.pinlines[i].strip() + '\n')

        if hasattr(self.data,'slaline'): # Water cross?
            f.write(self.data.slaline.strip() + '\n')

        f.write('LPI\n')
        for i in range(self.data.npst):
            for j in range(i+1):
                f.write('%d ' % self.data.LPI[i,j])
            f.write('\n')

        f.write(self.data.spa.strip() + '\n')
        depstr = "DEP 0, 0.001, -" + str(maxdep)
        f.write(depstr + '\n')

        f.write('NLI\n')
        f.write('STA\n')
        f.write('END\n')

        f.close()

    def add_calc(self): # Append a list element to store result of calculation
        self.data.append({'info':{}, 'statepoints':[]})

    def add_qcalc(self):
        self.db['qcalc'].append({'info':{}, 'statepoints':[]})

    def writec3cai(self, voi=None, maxdep=None):
        filebasename = "./" + str(uuid.uuid4())
        c3inp = filebasename + ".inp"
        #c3inp = tempfile.NamedTemporaryFile(dir='.',prefix="c3_",suffix=".inp",delete=False)
        print "Writing c3 input file " + c3inp
        
        info = self.data[0]['info'] # Get info data from original import
        if self.data[-1]['info'].has_key('LFU'):
            LFU = self.data[-1]['info'].get('LFU') # Get LFU from last calc
        else:
            print "Error: LFU is missing"
            return

        #info = self.db['origin']['info']
        #LFU = self.db['qcalc'][-1]['info'].get('LFU')
        
        #f = c3inp.file
        f = open(c3inp,'w')

        tit = "TIT "
        tit = tit + info.get('tfu').split('*')[0].replace(',','=').strip() + " "
        tit = tit + info.get('tmo').split('*')[0].replace(',','=').strip() + " "
        if voi == None:
            voivec = info.get('voi').split('*')[0].replace(',',' ').strip().split(' ')[1:]
            tit = tit + "VOI=" + voivec[0] + " "
            ide = ["'BD"+x+"'" for x in voivec]
            f.write(tit + "IDE=" + ide[0] + '\n')
        else:
            tit = tit + "VOI=" + str(voi) + " "
            f.write(tit + '\n')
        f.write(info.get('sim').strip() + '\n')
        
        FUE = info.get('FUE')
        Nfue = FUE.shape[0]
        for i in xrange(Nfue):
            f.write('FUE  %d ' % (FUE[i,0]))
            f.write('%5.3f/%5.3f' % (FUE[i,1],FUE[i,2]))
            if ~np.isnan(FUE[i,3]):
                f.write(' %d=%4.2f' % (FUE[i,3],FUE[i,4]))
            f.write('\n')
        
        f.write('LFU\n')
        for i in xrange(info.get('npst')):
            for j in range(i+1):
                f.write('%d ' % LFU[i,j])
            f.write('\n')
        
        pde = info.get('pde').split('\'')[0]
        f.write(pde.strip() + '\n')
        f.write(info.get('bwr').strip() + '\n')
        
        Npin = np.size(info.get('pinlines'))
        for i in xrange(Npin):
            tmpstr = re.split('\*|/',info.get('pinlines')[i].strip())[0]# Remove coments etc
            pinarr = re.split(',|\s+',tmpstr.strip()) # Split for segments
            npinsegs = len(pinarr)-2
            if npinsegs > 3:
                red_pinstr = ' '.join(pinarr[0:3]+pinarr[-2:])
            else:
                red_pinstr = info.get('pinlines')[i].strip()
            f.write(red_pinstr.strip() + '\n')

        if info.get('slaline'): # has water cross?
            f.write(info.get('slaline').strip() + '\n')
        
        f.write('LPI\n')
        for i in xrange(info.get('npst')):
            for j in xrange(i+1):
                f.write('%d ' % info.get('LPI')[i,j])
            f.write('\n')

        f.write(info.get('spa').strip() + '\n')
        if maxdep == None:
            f.write(info.get('dep').strip() + '\n')
        else:
            depstr = "DEP 0, 0.001, -" + str(maxdep)
            f.write(depstr + '\n')
            
        f.write('NLI\n')
        f.write('STA\n')

        if voi == None:
            N = len(ide)
            for i in xrange(1,N):
                f.write(tit + "IDE=" + ide[i] + '\n')
                res = "RES," + ide[i-1] + ",0"
                f.write(res + '\n')
                f.write("VOI " + voivec[i] + '\n')
                if maxdep == None:
                    f.write(info.get('dep').strip() + '\n')
                else:
                    depstr = "DEP 0, 0.001, -" + str(maxdep)
                    f.write(depstr + '\n')
                    
                f.write('STA\n')
        
        f.write('END\n')
        #c3inp.close()
        f.close()
        return filebasename


    def runc3(self,filebasename): # Running C3 perturbation model
        # C3 input file
        c3inp = filebasename + ".inp"
        #c3inp = "./c3.inp"
        # output file
        #c3out = tempfile.NamedTemporaryFile(dir='.',prefix="c3_",suffix=".out",delete=False)
        c3out = filebasename + ".out"
        # cax file
        c3cax = filebasename + ".cax"
        # libs
        lib1 = "./lib/c3/e4lbj40"
        lib2 = "./lib/c3/bal8ab4"
        lib3 = "./lib/c3/galb410"
        # C3 executable
        c3exe = "./bin/casmo3"

        # Write C3 configuration file
        #c3cfg = tempfile.NamedTemporaryFile(dir='.',prefix="c3_",suffix=".cfg",delete=False)
        c3cfg = filebasename + ".cfg"
        print c3cfg
        #c3cfg = "./c3.txt"
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
        #c3cfg.close()
        f.close()
        #Tracer()()
        # Run C3 executable
        #cmd = "linrsh " + c3exe + " " + c3cfg
        #cmd = c3exe + " " + c3cfg
        print "running c3 model"
        #os.system(cmd)
        try: # use linrsh if available
            call(['linrsh',c3exe,c3cfg])
        except:
            call([c3exe,c3cfg])

        # Remove files
        #c3cfg.unlink(c3cfg.name)
        os.remove(c3cfg)
        os.remove(c3inp)
        #c3out.unlink(c3out.name)
        os.remove(c3out)
        

    def readc3cax(self, filebasename, opt=None):
        
        c3cax = filebasename + ".cax"
        if not os.path.isfile(c3cax):
            print "Could not open file " + c3cax
            return
        else:
            print "Reading file " + c3cax

        # Read the whole file at once
        with open(c3cax) as f:
            flines = f.read().splitlines() #exclude \n
        self.__flines = flines
        
        # ------Search for regexp matches-------
        iTIT = self.__matchcontent('^TIT')
        iPOW = self.__matchcontent('POW\s+')
        iPOL = self.__matchcontent('^POL')
        
        # Read fuel dimension
        npst = int(flines[iPOW[0]+1][4:6])
        
        # ------Stepping through the state points----------
        Nburnpoints = len(iTIT)
        rvec = [re.split('[/\s+]+',flines[i+2].strip()) for i in iTIT]
        burnup = np.array([rvec[i][0] for i in xrange(Nburnpoints)]).astype(float)
        voi = np.array([rvec[i][1] for i in xrange(Nburnpoints)]).astype(float)
        vhi = np.array([rvec[i][2] for i in xrange(Nburnpoints)]).astype(float)
        tfu = np.array([rvec[i][3] for i in xrange(Nburnpoints)]).astype(float)
        tmo = np.array([rvec[i][5] for i in xrange(Nburnpoints)]).astype(float)

        # Row containing Kinf
        kinfstr = [flines[i+5] for i in iPOL]
        kinf = np.array([re.split('\s+',kinfstr[i].strip())[0] for i in xrange(Nburnpoints)]).astype(float)

        # Rows containing radial power distribution map
        powmap = [flines[i+2:i+2+npst] for i in iPOW]
        POW = np.array([self.__symtrans(self.__map2mat(powmap[i],npst)) for i in xrange(Nburnpoints)]).swapaxes(0,2)

        
        #Tracer()()
        #burnup = np.zeros(Nburnpoints); burnup.fill(np.nan)
        #voi = np.zeros(Nburnpoints); voi.fill(np.nan)
        #vhi = np.zeros(Nburnpoints); vhi.fill(np.nan)
        #tfu = np.zeros(Nburnpoints); tfu.fill(np.nan)
        #tmo = np.zeros(Nburnpoints); tmo.fill(np.nan)
        #kinf = np.zeros(Nburnpoints); kinf.fill(np.nan)
        #POW = np.zeros((npst,npst,Nburnpoints)); POW.fill(np.nan)
        
        # Row vector containing burnup, voi, vhi, tfu and tmo
        #rvec = [re.split('/',flines[i+2].strip()) for i in iTIT]

        # Row containing Kinf
        #kinfstr = [flines[i+5] for i in iPOL]

        # Rows containing radial power distribution map
        #powmap = [flines[i+2:i+2+npst] for i in iPOW]

        #for i in range(Nburnpoints):
        #    # Read burnup, voids, tfu and tmo
        #    burnup[i],voi[i] = re.split('\s+',rvec[i][0].strip())
        #    vhi[i],tfu[i] = re.split('\s+',rvec[i][1].strip())
        #    tmo[i] = re.split('\s+',rvec[i][2].strip())[1]
        #    # Read kinf
        #    kinf[i] = re.split('\s+',kinfstr[i].strip())[0]
        #    # Read radial power distribution map
        #    POW[:,:,i] = self.__symtrans(self.__map2mat(powmap[i],npst))

        # Calculate radial burnup distributions
        EXP = self.__expcalc(POW,burnup)
        # Calculate Fint:
        fint = self.__fintcalc(POW)

        # Append state instancies
        statepoints = [{'burnup':burnup[i],'voi':voi[i],'vhi':vhi[i],'tfu':tfu[i],\
                        'tmo':tmo[i],'kinf':kinf[i],'fint':fint[i],'EXP':EXP[:,:,i],\
                        'POW':POW[:,:,i]} for i in xrange(Nburnpoints)]

        #Tracer()()
        #self.qcalc.append(datastruct())
        #pindex = -1 # Index of last instance
        #self.qcalc[pindex].model = "c3"
        #self.qcalc[pindex].statepoints = []
        #for i in range(Nburnpoints):
        #    self.qcalc[pindex].statepoints.append(datastruct()) # append new instance to list
        #    self.qcalc[pindex].statepoints[i].burnup = burnup[i]
        #    self.qcalc[pindex].statepoints[i].voi = voi[i]
        #    self.qcalc[pindex].statepoints[i].vhi = vhi[i]
        #    self.qcalc[pindex].statepoints[i].tfu = tfu[i]
        #    self.qcalc[pindex].statepoints[i].tmo = tmo[i]
        #    self.qcalc[pindex].statepoints[i].kinf = kinf[i]
        #    self.qcalc[pindex].statepoints[i].fint = fint[i]
        #    self.qcalc[pindex].statepoints[i].POW = POW[:,:,i]
        #    self.qcalc[pindex].statepoints[i].EXP = EXP[:,:,i]

        # Append statepoints to data attribute
        if opt == 'refcalc': # add to refcalc dictionary field
            self.data[0]['refcalc']['statepoints'] = statepoints
        else:
            self.data[-1]['statepoints'] = statepoints

        # Append statepoints to db
        #self.db['qcalc'][-1]['statepoints'] = statepoints
        os.remove(c3cax)

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

    def __expcalc(self,POW,burnup):
        Nburnpoints = burnup.size
        npst = POW.shape[0]
        EXP = np.zeros((npst,npst,Nburnpoints)); EXP.fill(np.nan)
        for i in range(Nburnpoints):
            if burnup[i] == 0:
                EXP[:,:,i] = 0
            else:
                dburn = burnup[i] - burnup[i-1]
                if dburn < 0:
                    EXP[:,:,i] = POW[:,:,i]*burnup[i]
                else:
                    EXP[:,:,i] = EXP[:,:,i-1] + POW[:,:,i]*dburn
        return EXP

    def __fintcalc(self,POW):
        Nburnpoints = POW.shape[2]
        fint = np.zeros(Nburnpoints); fint.fill(np.nan)
        for i in range(Nburnpoints):
            fint[i] = POW[:,:,i].max()
        return fint

    def findpoint(self,burnup=None,vhi=None,voi=None,tfu=None):
        """Return statepoint index that correspond to specific burnup, void and void history
        Syntax: pt = findpoint(burnup=burnup_val,vhi=vhi_val,voi=voi_val,tfu=tfu_val)"""

        if tfu is not None:
            pindex = next(i for i,p in enumerate(self.statepoints) if p.tfu==tfu)
        elif burnup is not None:
            pindex = next(i for i,p in enumerate(self.statepoints)
                          if p.burnup==burnup and p.vhi==vhi and p.voi==voi)
        else:
            pindex = next(i for i,p in enumerate(self.statepoints)
                          if p.vhi==vhi and p.voi==voi)    
        return pindex

        

if __name__ == '__main__':
    casdata(sys.argv[1])
