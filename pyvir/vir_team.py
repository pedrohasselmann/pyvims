# -*- coding: utf-8 -*-
import os
import numpy as np
from datetime import datetime as dt
import pvl

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
        if self.lbl['QUBE']['CORE_ITEM_TYPE'] == 'SUN_INTEGER':
            arch = '>' # Big endian
        else:
            arch = '<' # Little endian

        if int(self.lbl['QUBE']['CORE_ITEM_BYTES']) == 2:
            byte = 'i2'
        elif int(self.lbl['QUBE']['CORE_ITEM_BYTES']) == 4:
            byte = 'f'
        else:
            raise ValueError('Unknown CORE_ITEM_BYTES')

        dtype = np.dtype(arch+byte)
        IDFoffset = (int(self.lbl['^HISTORY']) - 1) * int(self.lbl['RECORD_BYTES'])
        nbytes = self.NS * int(self.lbl['QUBE']['CORE_ITEM_BYTES'])

        cube = np.zeros((self.NB, self.NL, self.NS))
        with open(self.fname) as f:
            f.seek(IDFoffset, os.SEEK_SET) # Skip Ascii header

            if self.lbl['QUBE']['AXIS_NAME'] == ('SAMPLE', 'BAND', 'LINE'):
                for line in xrange(self.NL):
                    for band in xrange(self.NB):
                        sample = np.frombuffer(f.read(nbytes),dtype=dtype) # Read image sample
                        cube[band, line, :] = sample
            elif self.lbl['QUBE']['AXIS_NAME'] == ('SAMPLE', 'LINE', 'BAND'):
                for band in xrange(self.NB):
                    for line in xrange(self.NL):
                        sample = np.frombuffer(f.read(nbytes),dtype=dtype) # Read image sample
                        cube[band, line, :] = sample
            elif self.lbl['QUBE']['AXIS_NAME'] == ('BAND', 'SAMPLE', 'LINE'):
                for band in xrange(self.NL):
                    for line in xrange(self.NS):
                        sample = np.frombuffer(f.read(nbytes),dtype=dtype) # Read image sample
                        cube[band, line, :] = sample

        self.cube = cube
        return
