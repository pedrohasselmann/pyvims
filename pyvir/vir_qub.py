# -*- coding: utf-8 -*-
import os

from .vir_team import VIR_TEAM

class VIR_QUB(VIR_TEAM):
    def __init__(self, imgID):
        VIR_TEAM.__init__(self, imgID)
        return

    def __repr__(self):
        return "DAWN VIR cube: %s [QUB]" % self.imgID

    @property
    def fname(self):
        '''Check if VIMS file exists.'''
        fname = self.imgID + '.QUB'
        if not os.path.isfile(fname):
            raise NameError('PDS QUB file was not found: %s' % fname)
        return fname
