"""Module to provide IO support for reading and writing 
compressed and uncompressed files
"""

import io
import sys
import locale
import warnings

__all__ = ('open','STDIO')

from os.path import expanduser
from urllib.parse import urlparse
from urllib.request import urlopen
from .filenames import infer_compression_format_by_suffix
from .constants import (
    get_preferred_gz_api,
    set_preferred_gz_api
)
from .constants import (
    _PYTHON_VERSION, 
    COMPRESSION_NAME_MAP,
    STDIO,
    BZIP2_MAGIC_NUMBER,
    BGZF_MAGIC_NUMBER, 
    COMPRESS_MAGIC_NUMBER, 
    GZIP_MAGIC_NUMBER, 
    XZ_MAGIC_NUMBER,
    ZIP_MAGIC_NUMBER, 
    ZSTD_MAGIC_NUMBER,
)

# NOTES:
# - See: https://docs.python.org/3/library/archiving.html for algorithm details
#
# - the compression modules (gzip, lzma, bz2file) accept file-like inputs,
#   even _io.TextIOWrapper objects for opening
#
# - the compression modules (gzip, lzma, bz2file) wrap the opened file
#   objects in _io.TextIOWrapper objects when 't' mode is requested
#
# - sys.stdin, sys.stderr, sys.stdout are _io.TextIOWrapper objects and
#   _io.TextIOWrapper cannot wrap another _io.TextIOWrapper object


def is_stream(fileobj):
    return hasattr(fileobj, '__next__') and hasattr(fileobj, 'close')



def infer_encoding(encoding=None):
    return locale.getpreferredencoding(False) if encoding is None else encoding



def infer_compression_format_by_magic_number(filename):
    with open(filename, 'rb') as fileobj:
        file_contents = fileobj.read(2)  # read first 2 bytes
        if file_contents.startswith(GZIP_MAGIC_NUMBER):
            file_contents += fileobj.read(2)
            if file_contents.startswith(BGZF_MAGIC_NUMBER):
                return 'bgzip'
            return 'gzip'
        elif file_contents.startswith(COMPRESS_MAGIC_NUMBER):
            raise NotImplementedError("compress/decompress format")
 
        file_contents += fileobj.read(1)  # append third byte
        if file_contents.startswith(BZIP2_MAGIC_NUMBER):
            return 'bzip2'
 
        file_contents += fileobj.read(1)  # append fourth byte
        if file_contents.startswith(ZSTD_MAGIC_NUMBER):
            return 'zstd'
        elif file_contents.startswith(ZIP_MAGIC_NUMBER):
            return 'zip'

        file_contents += fileobj.read(2)  # append fifth and sixth bytes
        if file_contents.startswith(XZ_MAGIC_NUMBER):
            return 'lzma'
    return None



def import_compression_module(module):
    if type(module) == "module":
        # already loaded, pass-through
        module_object = module
    elif module is None:
        import io as module_object
    else:
        module = module.lower()
        if module in COMPRESSION_NAME_MAP:
            if COMPRESSION_NAME_MAP[module] == 'bgzip':
                try:
                    import bgzip as module_object
                except ImportError:
                    warnings.warn(
                        "bgzip module not found, falling back to gzip"
                    )
                    # import gzip as module_object
                    return import_compression_module('gzip')
                
            elif COMPRESSION_NAME_MAP[module] == 'bzip2':
                if _PYTHON_VERSION < (3,3):
                    # stdlib bz2 module did not support multistream
                    # prior to python 3.3; bz2file NOT in python stdlib
                    try:
                        import bz2file as module_object
                    except ImportError:
                        warnings.warn(
                            "bz2file module not found, falling back to bz2 "
                            "(multistream may not be supported)"
                        )
                        import bz2 as module_object
                elif _PYTHON_VERSION < (3,14):
                    import bz2 as module_object
                else:
                    from compression import bz2 as module_object

            elif COMPRESSION_NAME_MAP[module] == 'gzip':
                if _PYTHON_VERSION < (3,14):
                    import gzip as module_object
                else:
                    from compression import gzip as module_object
                    
            elif COMPRESSION_NAME_MAP[module] == 'zip':
                # use the package-local zipfile shunt implemented in
                # compression/zipfile.py so the package can open a member
                # inside a .zip archive transparently.
                from . import zipfile as module_object
                
            elif COMPRESSION_NAME_MAP[module] == 'zstd':
                if _PYTHON_VERSION < (3,14):
                    from backports import zstd as module_object
                else:
                    from compression import zstd as module_object
            else:
                try:
                    module_object = __import__(COMPRESSION_NAME_MAP[module])
                except ImportError:
                    raise ValueError(
                        "Unsupported format: %r" % module
                    )
        else:
            try:
                module_object = __import__(module)
            except ImportError:
                raise ValueError(
                    "Unsupported format: %r" % module
                )
    return module_object



def open(filename, mode='rt', compresslevel=0, encoding=None, errors=None, newline=None, compression=None):
    """Open a gzip-/bgzip-/bzip2-/lzma-/xz-compressed file or uncompressed file
    in binary or text mode.

    The `filename` argument can be an actual filename (a str or bytes object), 
    or an existing file object to read from or write to. Use "-" to open a file
    object to the appropriate stdin/stdout stream requested via `mode`. Serial
    reading via HTTP and FTP URL file path is supported, but writing is not.

    The `mode` argument can be "r", "rb", "w", "wb", "x", "xb", "a" or "ab" for
    binary mode, or "rt", "wt", "xt" or "at" for text mode. The default mode is
    "rt". The default `compresslevel` for compression streams is 9.

    For binary mode, the `encoding`, `errors`, and `newline` arguments must not
    be provided.

    For text mode, a compressed stream object is created, then wrapped in an
    io.TextIOWrapper instance with the specified encoding, error handling
    behavior, and line ending(s).

    To read from/write to compressed streams from stdin/stdout or existing
    file-like objects, the appropriate compression module name or object must
    be passed via the `compression` agrument (e.g., compression='gzip' or 
    compression=gzip). When writing, `compresslevel` must be set to a value 
    between 1 and 9, inclusive (default is 9).

    This module relies on the `io`, `gzip`, `lzma`, `bz2` (or `bz2file`),
    `pysam` and `zstd` modules internally, but others can be supplied via the
    `compression` argument, which must return an object with a callable `open()`
    attribute. The `bz2file` module is only required for Python versions earlier
    than 3.3. The `zstd` module is available via the `backports` module prior to
    Python 3.14 and the `compression` module thereafter.
    
    See Also: help(io.open)
    """
    compressformat = infer_compression_format_by_suffix(filename)
    encoding = infer_encoding(encoding)
    
    if compression:
        if isinstance(compression, (str, bytes)):
            compressformat = compression
            compression = import_compression_module(compressformat)
        else:
            compressformat = compression.__name__.split('.')[-1]
    elif compressformat:
        compression = import_compression_module(compressformat)

    if compression is None or compression == io or compressformat == 'io':
        compressformat = None
        compression = None
    
    # Unless we explicitly request binary mode, default to
    # text mode. gzip, lzma, bz2, and bz2file default to 'rb',
    # so set 'rt' explicitly for a consistent interface:
    binmode = 'b' in mode
    if 'r' in mode:
        mode = 'r'
    else:
        if 'a' in mode:
            mode = 'a'
        elif 'x' in mode:
            mode = 'x'
        elif 'w' in mode:
            mode = 'w'
        else:
            raise ValueError("Invalid mode: %r" % mode)

        if compressformat:
            if not compresslevel:
                compresslevel = 9
        if compresslevel:
            if not (1 <= compresslevel <= 9):
                raise ValueError("compresslevel must be between 1 and 9")

    if binmode:
        mode += 'b'
    else:
        mode += 't'

    # Now define appropriate options for the compression:
    options = {
        'errors' : errors,
        'newline': newline
    }
    if compresslevel:
        if compressformat == 'xz' or \
           compressformat == 'lzma':
            options['preset'] = compresslevel
        elif compressformat == 'zstd':
            options['level'] = compresslevel
        else:
            options['compresslevel'] = compresslevel
    elif not binmode:
        options['encoding'] = encoding

    # Lastly, open the file (if necessary)
    if is_stream(filename):
        # bgzip does not permit input streams...
        if hasattr(filename, 'buffer'):
            # To use a compression() with our input/output stream,
            # use stream.buffer, as std streams decode bytes
            # to str under the hood automatically:
            # https://stackoverflow.com/questions/53245314/python-read-gzip-from-stdin
            filename = filename.buffer
        if compression:
            if compressformat == 'bgzip':
                warnings.warn(
                    "bgzip does not support inputting existing streams; "
                    "opening with gzip. If this is not desired, open the "
                    "file with compression.open() directly."
                )
                compressformat = 'gzip'
                compression = import_compression_module(compressformat)
        else:
            return io.TextIOWrapper(filename, **options)
        
    elif filename == STDIO:
        fileobj = sys.stdin if 'r' in mode else sys.stdout
        if compression:
            if compressformat == 'bgzip':
                pass
            else:
                filename = fileobj.buffer
        else:
            return fileobj  # already an io.TextIOWrapper object
    else:
        url = urlparse(filename)
        if 'ftp' in url.scheme or 'http' in url.scheme:
            if compressformat:
                if compressformat == 'bgzip':
                    pass  # bgzip opens URL path files natively, defer to it.
                else:
                    filename = urlopen(filename)
            elif 'r' in mode:
                return io.TextIOWrapper(urlopen(filename), **options)
            else:
                raise TypeError("URL streams not writeable")
        else:
            filename = expanduser(filename)

    options['mode'] = mode
    if not compression:
        compression = io

    return compression.open(filename, **options)


#TODO: add snappy and lz4 support
#TODO: bgzip reader raises UnicodeDecodeError: 'utf-8' codec can't decode bytes in position 8-10: invalid continuation byte
