# -*- coding: utf-8 -*-
import os
import numpy as np
import cv2

def getImgID(imgID):
    '''Extract img identification number'''
    return imgID.lower()\
                .split(os.sep)[-1]\
                .replace('cm_','')\
                .replace('_ir','')\
                .replace('_vis','')\
                .replace('.cub','')\
                .replace('.qub','')\
                .replace('.nav','')\
                .replace('.lbl','')\
                .replace('c','')\
                .replace('v','')

def clipIMG(img, imin=0, imax=None):
    '''Clip image [0-255] between imin/imax'''
    if imax is None:
        imax = np.nanmax(img)
    return np.uint8(np.clip(255.*(img-imin)/(imax-imin), 0, 255))

def imgInterp(img, imin=0, imax=None, height=256, hr='NORMAL',
              method=cv2.INTER_LANCZOS4, equalizer=True):
    '''
    Interpolate image

    hr:
        High-Resolution mode in Sample direction ['NORMAL'|'HI-RES']
    
    method:
    - INTER_NEAREST - a nearest-neighbor interpolation
    - INTER_LINEAR - a bilinear interpolation
    - INTER_AREA - resampling using pixel area relation.
    - INTER_CUBIC - a bicubic interpolation over 4x4 pixel neighborhood
    - INTER_LANCZOS4 - a Lanczos interpolation over 8x8 pixel neighborhood
    '''
    if img.dtype != 'uint8':
        img = clipIMG(img, imin, imax)

    if not height is None:
        hr = 1 if hr.upper() == 'NORMAL' else 2
        width = (height * img.shape[0]) / img.shape[1] / hr
        img = cv2.resize(img, (width, height), interpolation=method)

    if equalizer:
        # Create a CLAHE object.
        clahe = cv2.createCLAHE(clipLimit=1, tileGridSize=(2, 2))
        img = clahe.apply(img)
    return img