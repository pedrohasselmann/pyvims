# -*- coding: utf-8 -*-
import os
import numpy as np
from datetime import datetime as dt
import pvl
import struct

class VIR_TEAM(object):
    def __init__(self, imgID):
        self.imgID = imgID #VIMS_OBJ.__init__(self, imgID, root)
        self.readLBL()
        self.readCUB()
        #self.setNAV()
        return

    def __repr__(self):
        return "DAWN VIR cube: %s [TEAM]" % self.imgID

    def readLBL(self):
        '''Read VIMS LBL header'''
        self.lbl = pvl.load(self.imgID+'.LBL')

        for ii, axis in enumerate(self.lbl['QUBE']['AXIS_NAME']):
            if axis == 'SAMPLE':
                self.NS = int(self.lbl['QUBE']['CORE_ITEMS'][ii])
            elif axis == 'LINE':
                self.NL = int(self.lbl['QUBE']['CORE_ITEMS'][ii])
            elif axis == 'BAND':
                self.NB = int(self.lbl['QUBE']['CORE_ITEMS'][ii])

        self.obs    = self.lbl['INSTRUMENT_HOST_NAME']
        self.inst   = self.lbl['INSTRUMENT_ID']
        self.target = self.lbl['TARGET_NAME']
        self.expo = self.lbl['FRAME_PARAMETER'][0]
        #self.mode = self.lbl['QUBE']['SAMPLING_MODE_ID'][0]
        #self.seq    = self.lbl['QUBE']['SEQUENCE_ID']
        #self.seq_title = self.lbl['QUBE']['SEQUENCE_TITLE']
        self.start  = self.lbl['START_TIME']
        self.stop   = self.lbl['STOP_TIME']
        self.dtime  = (self.stop - self.start)/2 + self.start
        self.time   = self.dtime.strftime('%Y-%m-%dT%H:%M:%S.%f')
        self.year   = self.dtime.year
        self.doy    = int(self.dtime.strftime('%j'))
        self.year_d = self.year + (self.doy-1)/365. # Decimal year [ISSUE: does not apply take into account bissextile years]
        self.date   = self.dtime.strftime('%Y/%m/%d')

        self.wvlns = np.array(self.lbl['QUBE']['BAND_BIN']['BAND_BIN_CENTER'])
        self.bands = np.array(self.lbl['QUBE']['BAND_BIN']['BAND_BIN_ORIGINAL_BAND'])
        return

    def readCUB(self):
        '''Read VIMS CUB data file'''
        if self.lbl['QUBE']['CORE_ITEM_TYPE'] == 'IEEE_REAL':
            arch = '>' # Big endian
        else:
            arch = '<' # Little endian

        if int(self.lbl['QUBE']['CORE_ITEM_BYTES']) == 2:
            byte = 'i2'
        elif int(self.lbl['QUBE']['CORE_ITEM_BYTES']) == 4:
            byte = 'f'
        else:
            raise ValueError('Unknown CORE_ITEM_BYTES')

        dtype = np.dtype('>'+byte)
        IDFoffset = (int(self.lbl['^HISTORY']) -1) * int(self.lbl['RECORD_BYTES'])
        nbytes = int(self.lbl['QUBE']['CORE_ITEM_BYTES'])

        cube = np.zeros((self.NB, self.NS, self.NL))
        with open(self.fname, 'rb') as f:
            
            recByte = int(self.lbl['RECORD_BYTES'])
            dataPos = self.lbl['^HISTORY'] -1  # Data Pointer
            dim     = self.lbl['QUBE']['CORE_ITEMS']
            sfxItem = self.lbl['QUBE']['SUFFIX_ITEMS']
            crType  = self.lbl['QUBE']['CORE_ITEM_TYPE']
            crByte  = int(self.lbl['QUBE']['CORE_ITEM_BYTES'])

            print(dim, type(dim))
            print(sfxItem, type(sfxItem))
            print(crType, type(crType))

            if crType == "REAL" or crType == "IEEE_REAL":
               tp='f'
       

            coreBlock=(dim[0]+sfxItem[0]-1)*(dim[1]+sfxItem[1]-1)*(dim[2]-1)*crByte
            shape=(dim[0]+sfxItem[0]-1,(dim[1]+sfxItem[1]-1),dim[2]-1)
            lineDim=dim[2]*crByte

            dataStruc=str(dim[0]-1)+tp+sfxItem[0]*'L'
            d=(dim[1]+sfxItem[1]-1)*(dim[2]-1)*dataStruc
            
            #print(coreBlock)
            #print(shape)
            #print(dataStruc)

            #fl=open(self.fname,'rb')
            f.seek(dataPos*recByte, os.SEEK_SET)
            buff=f.read()
            out=struct.unpack_from(arch+d,buff)
            
            cube=np.array(out, dtype=np.float32).reshape(shape,order='F')[0:dim[0],:,:]
            
            #print(cube)
            
            
            '''
            f.seek(IDFoffset, os.SEEK_SET) # Skip Ascii header
            
            if self.lbl['QUBE']['AXIS_NAME'] == ['SAMPLE', 'BAND', 'LINE']:
                for line in range(self.NL):
                    for band in range(self.NB):
                        sample = np.frombuffer(f.read(self.NS*nbytes),dtype=dtype) # Read image sample
                        cube[band, line, :] = sample
                        
            elif self.lbl['QUBE']['AXIS_NAME'] == ['SAMPLE', 'LINE', 'BAND']:
                for band in range(self.NB):
                    for line in range(self.NL):
                        sample = np.frombuffer(f.read(self.NS*nbytes),dtype=dtype) # Read image sample
                        cube[band, line, :] = sample
                        
            elif self.lbl['QUBE']['AXIS_NAME'] == ['BAND', 'SAMPLE', 'LINE']:
                for line in range(self.NL):
                    for sample in range(self.NS):
                        band = np.frombuffer(f.read(self.NB*nbytes),dtype=dtype) # Read image sample
                        #cube[:, sample, line] = band
            '''
        self.cube = cube
        return
