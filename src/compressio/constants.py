
import sys

_EMPTY = ''
_PYTHON_VERSION = sys.version_info[:2]

STDIO = '-'

COMPRESSION_SUFFIX = {
    'bgzip' : ('.bgzip','.bgzf','.bgz','.gz'),
    'bzip2' : ('.bzip2','.bz2','.bz'),
    'gzip'  : ('.gzip','.gz','-gz','.z','-z','_z'),
    'lzma'  : ('.lzma','.lz','.xz'),
    'zstd'  : ('.zst',),
}

# snappy? lz4?
# zlib covered by gzip
COMPRESSION_NAME_MAP = {
    'lzma'    : 'lzma',
    'xz'      : 'lzma',
    'gzip'    : 'gzip',
    'gz'      : 'gzip',
    'bzip2'   : 'bzip2',
    'bz2file' : 'bzip2',
    'bz2'     : 'bzip2',
    'bgzip'   : 'bgzip',
    'bgzf'    : 'bgzip',
    'bgz'     : 'bgzip',
    'zstd'    : 'zstd',
    'zst'     : 'zstd',
}


BGZF_MAGIC_NUMBER = b'\x1f\x8b\x08\x04'
BZIP2_MAGIC_NUMBER = b'BZh'
GZIP_MAGIC_NUMBER = b'\x1f\x8b'
XZ_MAGIC_NUMBER = b'\xfd\x37\x7a\x58\x5a\x00'
ZIP_MAGIC_NUMBER = b'\x50\x4b\x03\x04'
ZSTD_MAGIC_NUMBER = b'\x28\xb5\x2f\xfd'
COMPRESS_MAGIC_NUMBER = b'\x1f\x9d'

_PREFERRED_GZ_API = 'gzip'


def set_preferred_gz_api(api_name):
    global _PREFERRED_GZ_API
    if api_name not in ('gzip', 'bgzip'):
        raise ValueError("Unsupported gz API: %r" % api_name)
    _PREFERRED_GZ_API = api_name


def get_preferred_gz_api():
    return _PREFERRED_GZ_API
