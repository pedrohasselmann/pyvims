PyVIMS
======

|Build| |Python| |Status| |Version| |License|

|Conda| |PyPI| |Docker| |Binder|

.. |Build| image:: https://travis-ci.org/seignovert/pyvims.svg?branch=master
        :target: https://travis-ci.org/seignovert/pyvims
.. |Python| image:: https://img.shields.io/pypi/pyversions/pyvims.svg?label=Python
        :target: https://pypi.org/project/pyvims
.. |Status| image:: https://img.shields.io/pypi/status/pyvims.svg?label=Status
        :target: https://pypi.org/project/pyvims
.. |Version| image:: https://img.shields.io/pypi/v/pyvims.svg?label=Version
        :target: https://pypi.org/project/pyvims
.. |License| image:: https://img.shields.io/pypi/l/pyvims.svg?label=License
        :target: https://pypi.org/project/pyvims
.. |Conda| image:: https://img.shields.io/badge/conda|seignovert-pyvims-blue.svg?logo=python&logoColor=white
        :target: https://anaconda.org/seignovert/pyvims
.. |PyPI| image:: https://img.shields.io/badge/PyPI-pyvims-blue.svg?logo=python&logoColor=white
        :target: https://pypi.org/project/pyvims
.. |Docker| image:: https://badgen.net/badge/docker|seignovert/pyvims/blue?icon=docker
        :target: https://hub.docker.com/r/seignovert/pyvims
.. |Binder| image:: https://badgen.net/badge/Binder/Live%20Demo/blue?icon=terminal
        :target: https://mybinder.org/v2/gh/seignovert/pyvims/master?filepath=playground.ipynb


Python package to manipulate the Cassini VIMS & DAWN VIR data.

pedrohasselmann edit: added some new adapted classes for reading DAWN VIR .QUB data.


Install
-------

With ``conda``
~~~~~~~~~~~~~~

Add conda-forge channel:

.. code:: bash

    $ conda config --add channels conda-forge

Install ``pyvims`` package:

.. code:: bash

    $ conda install -c seignovert pyvims


With ``pip``
~~~~~~~~~~~~

This module use ``OpenCV``, ``GDAL`` and ``Basemap`` libraries.
Depending on your operating system you need to install them first.
In python you should be able to do:

.. code:: python

    >>> import cv2
    >>> import osgeo
    >>> from mpl_toolkits.basemap import Basemap

Then you can install ``pyvims``

.. code:: bash

    $ pip install pyvims

With ``docker``
~~~~~~~~~~~~~~~
A docker image is available on the
`docker hub <https://hub.docker.com/r/seignovert/pyvims>`_.

.. code:: bash

    docker run --rm -it \
                -p 8888:8888 \
                -v $VIMS_DATA:/home/nbuser/data \
                -v $CASSINI_KERNELS:/home/nbuser/kernels \
                seignovert/pyvims

Examples
--------
Download a files from:
https://sbnarchive.psi.edu/pds3/dawn/vir/DWNVVIR_V1B_v2/DATA/20110811_SURVEY/20110823_CYCLE5/VIR_VIS_1B_1_367420939_3.LBL
https://sbnarchive.psi.edu/pds3/dawn/vir/DWNVVIR_V1B_v2/DATA/20110811_SURVEY/20110823_CYCLE5/VIR_VIS_1B_1_367420939_3.QUB

Then, simply do:

.. code:: python

    >>> from pyvims import pyvir
    >>> from matplotlib import pyplot as plt

    >>> qub = pyvir.VIR_QUB(path.join(your_home,your_path,'VIR_VIS_1B_1_367420939_3'))

    >>> qub
    VIR cube: VIR_VIS_1B_1_367420939_3 [ISIS3]

    >>> qub.cube.shape
    (432, 16, 256)

    >>> plt.imshow(qub.cube[100,:,:])
    >>> plt.show()

For more details, take a look to the
`static Jupyter NoteBook <https://nbviewer.jupyter.org/github/seignovert/pyvims/blob/master/pyvims.ipynb>`_
where more examples of usage are provided. You can also try this
`live demo on Binder <https://mybinder.org/v2/gh/seignovert/pyvims/master?filepath=playground.ipynb>`_.


Disclaimer
----------
This project is not supported or endorsed by either JPL, NAIF or NASA. The code is provided "as is", use at your own risk.
