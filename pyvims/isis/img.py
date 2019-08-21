"""VIMS image module."""

import numpy as np

import matplotlib.pyplot as plt


def _clip(img, imin=None, imax=None):
    """Clip image plane from 0 to 255 between imin and imax.

    Parameters
    ----------
    img: np.array
        Input 2D data plane.
    imin: float, optional
        Custom minimum clipping value.
    imax: float, optional
        Custom maximum clipping value.

    Returns
    -------
    np.array
        8 bits clipped image plane.

    """
    if imin is None:
        imin = np.nanmin(img)

    if imax is None:
        imax = np.nanmax(img)

    return np.uint8(np.clip(255 * (img - imin) / (imax - imin), 0, 255))


def rgb(r, g, b):
    """Create RGB 8 bits image from 3 channels.

    Parameters
    ----------
    r: np.array
        Red image plane data.
    g: np.array
        Green image plane data.
    b: np.array
        Blue image plane data.

    Returns
    -------
    np.array
        8 bits RGB image.

    """
    return np.moveaxis(np.vstack([
        [_clip(r)], [_clip(g)], [_clip(b)]
    ]), 0, 2)


def save_img(fname, data, npix=256, quality=65, interp='bicubic'):
    """Save JPG image from data array."""
    if np.ndim(data) == 2:
        w, h = np.shape(data)
    elif np.ndim(data) == 3:
        w, h, _ = np.shape(data)
    else:
        raise ValueError('Data must be a 2D or 3D array.')

    if w > h:
        nx = 1
        ny = h / w
    else:
        nx = w / h
        ny = 1

    fig = plt.figure(frameon=False, dpi=256, figsize=(nx, ny))

    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)

    ax.imshow(data, cmap='gray', interpolation=interp)

    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    fig.savefig(fname, quality=quality, bbox_inches='tight', pad_inches=0)
    plt.close()