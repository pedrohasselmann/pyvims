# -*- coding: utf-8 -*-
import os
import numpy as np
from datetime import datetime as dt

from ._communs import getImgID

NaN = -99999.

class VIMS_NAV(object):
    def __init__(self,imgID, root=''):
        self.imgID = getImgID(imgID)
        self.root  = root
        self.readLBL()
        self.readNAV()
        return

    def __repr__(self):
        return "VIMS geocube: %s" % self.imgID

    def __str__(self):
        return self.imgID

    @property
    def fname(self):
        '''Check if VIMS file exists.'''
        fname = self.root + 'V' + self.imgID + '.nav'
        if not os.path.isfile(fname):
            raise NameError('GeoCube file %s not found')
        return fname

    def readLBL(self):
        '''Read VIMS geocube LBL'''
        with open(self.fname) as f:
            lbl = {}; self.IDFoffset = 0
            for line in f.readlines():
                self.IDFoffset += len(line)
                if line == 'END\r\n' or line == 'FIN\r\n' or line == 'FIN\n':
                    break
                elif 'AXIS_NAME' in line:
                    axisName = line.rstrip('\r\n')\
                                   .split(' = ')[1]\
                                   .replace('(','')\
                                   .replace(')','')\
                                   .split(',')

                elif 'CORE_ITEMS' in line:
                    coreItems = line.rstrip('\r\n')\
                                    .split('=')[1]\
                                    .replace('(','')\
                                    .replace(')','')\
                                    .split(',')

                elif 'CORE_ITEM_BYTES' in line:
                    self.coreItemBytes = int(line.rstrip('\r\n')
                                                 .split(' = ')[1])

                elif 'CORE_ITEM_TYPE' in line:
                    self.coreItemType = line.rstrip('\r\n')\
                                   .split(' = ')[1]

                elif 'START_TIME' in line and (not 'NATIVE' in line) and (not 'EARTH_RECEIVED' in line):
                    self.start = dt.strptime(
                                    line.rstrip('\r\n')\
                                    .split(' = ')[1]\
                                    .replace('"',''),
                                    '%Y-%jT%H:%M:%S.%fZ')

                elif 'STOP_TIME' in line and (not 'NATIVE' in line) and (not 'EARTH_RECEIVED' in line):
                    self.stop = dt.strptime(
                                    line.rstrip('\r\n')\
                                    .split(' = ')[1]\
                                    .replace('"',''),
                                    '%Y-%jT%H:%M:%S.%fZ')

                elif '.ker' in line:
                    self.flyby = int(line.rstrip('\r\n')[-8:-5])

        for ii, axis in enumerate(axisName):
            if axis == 'SAMPLE':
                self.NS = int(coreItems[ii])
            elif axis == 'LINE':
                self.NL = int(coreItems[ii])
            elif axis == 'BAND':
                self.NB = int(coreItems[ii])

        self.dtime  = (self.stop - self.start)/2 + self.start
        self.time   = self.dtime.strftime('%Y-%m-%dT%H:%M:%S.%f')
        self.year   = self.dtime.year
        self.doy    = int(self.dtime.strftime('%j'))
        self.year_d = self.year + (self.doy-1)/365. # Decimal year [ISSUE: doest not apply take into account bissextile years]
        self.date   = self.dtime.strftime('%Y/%m/%d')

        return

    def readNAV(self):
        '''Read VIMS geocube data'''
        # Read binary file
        if self.coreItemType == 'SUN_INTEGER':
            arch = '>' # Big endian
        else:
            arch = '<' # Little endian

        if self.coreItemBytes == 2:
            byte = 'i2'
        elif self.coreItemBytes == 4:
            byte = 'f'
        else:
            raise ValueError('Unknown CORE_ITEM_BYTES')

        dtype = np.dtype(arch+byte)
        nbytes = self.NS * self.NL * self.coreItemBytes

        shape = (self.NL, self.NS)

        with open(self.fname, 'rb') as f:
            f.seek(self.IDFoffset+2, os.SEEK_SET) # Skip Ascii header
            self.lon = np.frombuffer(f.read(nbytes),dtype=dtype).reshape(shape) #% 360 # Pixel central longitude [East]
            self.lat = np.frombuffer(f.read(nbytes),dtype=dtype).reshape(shape) # Pixel central latitude [North]

        self.lon.setflags(write=1)
        self.lat.setflags(write=1)

        self.nan = (self.lon == NaN)
        self.lon[self.nan] = np.nan
        self.lat[self.nan] = np.nan
        return
