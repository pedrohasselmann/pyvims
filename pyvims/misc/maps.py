"""Background maps module."""

import os
import re

from matplotlib.image import imread

from ..vars import ROOT_DATA


ROOT = root = os.path.join(ROOT_DATA, 'maps')


def parse(rexp, line):
    """Parse README line.

    Parameters
    ----------
    rexp: str
        Regular expression for parser.
    line: str
        Line to parse.

    Returns
    -------
    array
        Parsed value(s).

    Raises
    ------
    ValueError
        If not match was found.

    Example
    -------
    >>> parse(r'\d+', 'abc12def45')
    ['12', '45']

    """
    res = re.findall(rexp, line)
    if not res:
        raise ValueError(f'Invalid line: {line}')
    return res


def add(maps, keys, attr, value):
    """Add value(s) to maps dict.

    Parameters
    ----------
    maps: dict
        Global list of maps.
    keys: list
        List of file maps to append.
    attr: str
        Key value.
    value: any
        Value to append. If the value is a tuple, the values
        will loop according to ``keys`` index.

    Raises
    ------
    ValueError
        If the keys variable is ``None``.

    """
    if keys is None:
        raise ValueError('No map key(s) selected.')

    if isinstance(value, str) and value == 'None':
        return

    for i, key in enumerate(keys):
        if key not in maps.keys():
            maps[key] = {}
        maps[key][attr] = value[i] if isinstance(value, tuple) else value


def basename(fname):
    """Extract filename basename without extension.

    Parameters
    ----------
    fname: str
        Input filename

    Returns
    -------
    str
        File basename without extension.

    Example
    -------
    >>> basename('foo')
    'foo'
    >>> basename('foo.txt')
    'foo'
    >>> basename('test.foo.txt')
    'test.foo'
    >>> basename('test/foo.txt')
    'foo'
    >>> basename('/test/foo.txt')
    'foo'

    """
    return str(fname) if '.' not in str(fname) else \
        '.'.join(os.path.basename(str(fname)).split('.')[:-1])


def parse_readme(filename):
    """Parse README file.

    Parameters
    ----------
    filename: str
        README filename.

    Returns
    -------
    dict
        List of all the maps available in the README.

    """
    with open(filename, 'r') as f:
        lines = f.read().splitlines()

    maps = {}
    name = None
    keys = None
    for line in lines:
        if line.startswith('##'):
            name = line[2:].strip()
            keys = None

        elif line.startswith('* Filename:'):
            filenames = parse(r'`([\w\.\-\s/\\]+)`', line)

            files = tuple([os.path.basename(fname) for fname in filenames])
            roots = tuple([os.path.dirname(fname) for fname in filenames])

            keys = tuple([basename(f) for f in files])

            add(maps, keys, 'fname', files)
            add(maps, keys, 'root', roots)
            add(maps, keys, 'name', name)

        elif line.startswith('* Source:'):
            src, url = parse(r'\[([\w\.\-\s]*)\]\(([\w\.\-\s:/]*)\)', line)[0]

            add(maps, keys, 'src', src)
            add(maps, keys, 'url', url)

        elif line.startswith('* Extent:'):
            lon_1, lon_2, lat_1, lat_2 = parse(r'(-?\d+\.\d+|-?\d+)', line)
            extent = [float(lon_1), float(lon_2), float(lat_1), float(lat_2)]
            add(maps, keys, 'extent', extent)

        elif line.startswith('* Projection:'):
            projection = parse(r'`([\w\-_\s]+)`', line)[0]
            add(maps, keys, 'projection', projection.lower())

    return maps


def remove_from_readme(filename, fname):
    """Remove map from README file.

    Parameters
    ----------
    filename: str
        README filename.
    fname: str
        Filename to remove

    Returns
    -------
    dict
        List of all the maps available in the README.

    """
    with open(filename, 'r') as f:
        lines = f.read().splitlines()

    new = []
    buffer = []
    include = True
    for i, line in enumerate(lines):
        if line.startswith('##'):
            if buffer:
                new += buffer

            include = True
            buffer = []

        elif line.startswith('* Filename:'):
            filenames = parse(r'`([\w\.\-\s/\\]+)`', line)

            files = tuple([basename(fname) for fname in filenames])

            if fname in files:
                include = False
                buffer = []

        if include:
            buffer.append(line)

    if buffer:
        new += buffer

    with open(filename, 'w') as f:
        f.write('\n'.join(new))


class MapsDetails(type):
    """Map details parser."""

    __maps = {}

    def __repr__(cls):
        return '\n - '.join([
            f'<{cls.__name__}> Available: {len(cls)}',
            *cls.maps().keys()
        ])

    def __len__(cls):
        return len(cls.maps())

    def __contains__(cls, item):
        return item in cls.maps().keys()

    def __iter__(cls):
        return iter(cls.maps())

    def __getitem__(cls, item):
        try:
            return Map(**cls.maps()[item])
        except KeyError:
            raise KeyError(f'Unknown map `{item}`.')

    @classmethod
    def maps(cls):
        """Load all maps listed in content."""
        if not cls.__maps:
            cls.__maps = parse_readme(cls.filename())
        return cls.__maps

    @classmethod
    def filename(cls):
        """Get README filename.

        Raises
        ------
        FileNotFoundError
            If the file is missing.

        """
        filename = os.path.join(ROOT, 'README.md')

        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                f.write('\n'.join([
                    'List of maps available',
                    '======================\n',
                    '## Titan VIMS/ISS\n',
                    '* Filename: `Titan_VIMS_ISS.jpg`',
                    '* Source: [Seignovert et al. 2019](https://doi.org/10.22002/D1.1173)',
                    '* Extent: `-180° 180° -90° 90°`',
                    '* Projection: `equirectangular`\n',
                ]))

        return filename

    @classmethod
    def register(cls, m, update=False):
        """Register a new maps in README.

        Parameters
        ----------
        m: Map
            Background map object.
        update: bool, optional
            Enable map update with the same key.

        Raises
        ------
        TypeError
            If the map provided doest not have a
            ``markdown`` attribute.
        ValueError
            If the ``name`` attribute is already used.

        """
        if not hasattr(m, 'markdown'):
            raise TypeError(f'Map has an invalid type: `{type(m)}`.')

        key = basename(m)

        if key in cls.maps().keys():
            if update:
                cls.remove(key)
            else:
                raise ValueError(f'A map is already registered with the name: `{key}`.')

        with open(cls.filename(), 'a') as f:
            f.write(f'\n{m.markdown}')

        cls.__maps[key] = dict(m)

        print(f'Image `{key}` saved in map registry.')

    @classmethod
    def remove(cls, fname):
        """Remove a map file from README."""
        key = basename(fname)

        if key in cls.maps().keys():
            remove_from_readme(cls.filename(), key)
            del cls.__maps[key]


class MAPS(metaclass=MapsDetails):
    """List of all the registered maps."""


class Map:
    """Background map object.

    Image filename format:

        `ROOT`/`Target`_`INSTR`.`ext`

    Parameters
    ----------
    fname: str
        Image filename.
    root: str, optional
        Data root folder containing the map.
        If ``None`` is provided (default), the
        package ``maps`` folder will be used.

    """

    def __init__(self, fname, root=None, extent=None, src=None, url=None,
                 projection=None, name=None):
        self.root = root if root else ROOT
        self.fname = fname

        self.data_extent = extent
        self.src = src
        self.url = url
        self.proj = projection.lower() if isinstance(projection, str) else None

        self.name = name if name is not None else \
            '.'.join(self.fname.split('.')[:-1])

    def __str__(self):
        return self.fname if self.root == ROOT else self.filename

    def __repr__(self):
        return '\n - '.join([
            f'<{self.__class__.__name__}> {self}',
            f'Size: {self.img.shape}',
            f'Extent: {"Undefined" if self.data_extent is None else self.data_extent}',
            f'Source: {"Undefined" if self.src is None else self.src}',
            f'URL: {"Undefined" if self.url is None else self.url}',
            f'Projection: {"Undefined" if self.proj is None else self.proj.title()}',
        ])

    def __iter__(self):
        for k, v in self.as_dict.items():
            yield k, v

    @property
    def fname(self):
        return self.__fname

    @fname.setter
    def fname(self, fname):
        if os.path.dirname(fname):
            self.root = os.path.dirname(fname)

        self.__fname = os.path.basename(fname)
        self.__img = None

        if not os.path.exists(self.filename):
            raise FileNotFoundError(f'Map `{self.filename}` is not available.')

    @property
    def filename(self):
        """Image absolute path."""
        return os.path.join(self.root, self.fname)

    @property
    def extent_str(self):
        """Format data extent as string."""
        return ' '.join([f'{e}°' for e in self.data_extent])

    @property
    def markdown(self):
        """Convert Map object into markdown."""
        return '\n'.join([
            f'## {self.name}\n',
            f'* Filename: `{self}`',
            f'* Source: [{self.src}]({self.url})',
            f'* Extent: `{self.extent_str}`',
            f'* Projection: `{self.proj}`',
            f'\n![{self.name}]({self.filename})',
        ])

    @property
    def as_dict(self):
        """Convert as dict."""
        return {
            'name': self.name,
            'fname': self.fname,
            'root': self.root,
            'src': self.src,
            'url': self.url,
            'extent': self.data_extent,
            'projection': self.proj,
        }

    def register(self, update=False):
        """Register map in MAPS."""
        MAPS.register(self, update=update)

    @property
    def img(self):
        """Image data."""
        if self.__img is None:
            self.__img = imread(self.filename)
        return self.__img

    @property
    def extent(self):
        """Projected data extent."""
        if self.proj in [None, 'equi', 'equirectangular', 'plate carrée', 'lonlat']:
            return self.data_extent

        raise ValueError(f'Projection `{self.proj}` is not available.')
