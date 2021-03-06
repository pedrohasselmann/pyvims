"""VIMS ISIS header."""

import os

import numpy as np

import pvl

from .errors import ISISError
from .labels import ISISLabels
from .tables import ISISTables
from .time import time as _dt
from .vars import BYTE_ORDERS, FIELD_TYPES

class ISISCube:
    """VIMS ISIS header object.

    Parameters
    ----------
    filename: str
        Input ISIS filename.

    """

    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return self.filename

    def __repr__(self):
        return f'<{self.__class__.__name__}> ISIS Cube: {self}'

    def __contains__(self, key):
        return key in self.keys()

    def __getitem__(self, key):
        if key not in self:
            raise KeyError(f'Key `{key}` not found.')

        if key in self.labels:
            return self.labels[key]

        return self.tables[key]

    @property
    def filename(self):
        return self.__filename

    @filename.setter
    def filename(self, filename):
        self.__filename = filename
        self.__pvl = None
        self.__labels = None
        self.__tables = None
        self.__cube = None

        if not self.is_file:
            raise FileNotFoundError(f'File `{self.filename}` not found.')

        if not self.is_isis:
            raise ISISError(f'File `{self.filename}` is not in ISIS format.')

    @property
    def is_file(self):
        """Check if the file exists."""
        return os.path.exists(self.filename)

    @property
    def is_isis(self):
        """Check if the file is in ISIS format."""
        with open(self.filename, 'rb') as f:
            header = f.read(17)

        return header == b'Object = IsisCube'

    @property
    def pvl(self):
        """Full ISIS header in PVL format."""
        if self.__pvl is None:
            self.__pvl = pvl.load(self.filename)
        return self.__pvl

    @property
    def labels(self):
        """ISIS label labels."""
        if self.__labels is None:
            self.__labels = ISISLabels(self.pvl)
        return self.__labels

    @property
    def tables(self):
        """ISIS tables."""
        if self.__tables is None:
            self.__tables = ISISTables(self.filename, self.pvl)
        return self.__tables

    def keys(self):
        """ISIS labels and tables keys."""
        return list(self.labels.keys()) + list(self.tables.keys())

    @property
    def header(self):
        """Main ISIS Cube header."""
        return self.pvl['IsisCube']

    @property
    def _core(self):
        """ISIS core header."""
        return self.header['Core']

    @property
    def _dim(self):
        """ISIS dimension header."""
        return self._core['Dimensions']

    @property
    def NS(self):
        """Number of samples."""
        return self._dim['Samples']

    @property
    def NL(self):
        """Number of lines."""
        return self._dim['Lines']

    @property
    def NB(self):
        """Number of bands."""
        return self._dim['Bands']

    @property
    def shape(self):
        """Cube shape."""
        return (self.NB, self.NL, self.NS)

    @property
    def _pix(self):
        """ISIS core header."""
        return self._core['Pixels']

    @property
    def dtype(self):
        """Cube data type."""
        return np.dtype(
            BYTE_ORDERS[self._pix['ByteOrder']] +
            FIELD_TYPES[self._pix['Type']])

    @property
    def _start_byte(self):
        """Cube data start byte."""
        return self._core['StartByte'] - 1

    @property
    def _nbytes(self):
        """Cube data bytes size."""
        return self.NB * self.NL * self.NS * self.dtype.itemsize

    @property
    def _base(self):
        """Cube data base factor."""
        return self._pix['Base']

    @property
    def _mult(self):
        """Cube data multiplication factor."""
        return self._pix['Multiplier']

    @property
    def cube(self):
        """ISIS cube."""
        if self.__cube is None:
            self.__cube = self._load_data()
        return self.__cube

    def _load_data(self):
        """Load ISIS table data."""
        with open(self.filename, 'rb') as f:
            f.seek(self._start_byte)
            data = f.read(self._nbytes)

        data = np.frombuffer(data, dtype=self.dtype) * self._mult + self._base
        return np.reshape(data, self.shape)

    @property
    def _bands(self):
        """Cube band bin header."""
        return self.header['BandBin']

    @property
    def bands(self):
        """Cube bands numbers."""
        return np.array(self._bands['OriginalBand'])

    @property
    def wvlns(self):
        """Cube central wavelengths (um)."""
        return np.array(self._bands['Center'])

    @property
    def _inst(self):
        """Cube instrument header."""
        return self.header['Instrument']

    @property
    def start(self):
        """Instrument start time (UTC)."""
        return _dt(self._inst['StartTime'])

    @property
    def stop(self):
        """Instrument stop time (UTC)."""
        return _dt(self._inst['StopTime'])

    @property
    def duration(self):
        """Instrument acquisition dureation."""
        return self.stop - self.start

    @property
    def time(self):
        """Instrument mid time (UTC)."""
        return self.start + self.duration / 2
