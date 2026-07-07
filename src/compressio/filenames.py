
import os
from .constants import COMPRESSION_SUFFIX
from .constants import get_preferred_gz_api


def split_suffix(filename, suffixes=None):
    tempname = filename.lower()
    if isinstance(tempname, bytes):
        tempname = tempname.decode()
        
    if suffixes is None:
        if tempname.rfind(os.path.sep) < tempname.rfind(os.path.extsep):
            return tuple(filename.rsplit(os.path.extsep, maxsplit=1))
        else:
            return filename, None
        
    for suffix in sorted(suffixes, key=len, reverse=True):
        if isinstance(suffix, bytes):
            suffix = suffix.decode()
        if tempname.endswith(suffix):
            return filename[:-len(suffix)], filename[-len(suffix):]
        
    return filename, None



def strip_suffix(filename, suffixes=None):
    return split_suffix(filename, suffixes)[0]
    


def infer_compression_format_by_suffix(filename):
    """
    Infer from the filename extension the compression format used,
    or None.

    If passed a fileobj, returns None.
    """
    if isinstance(filename, (str, bytes)):
        tempname = filename.lower()
        if isinstance(tempname, bytes):
            tempname = tempname.decode()
        for fileformat in sorted(COMPRESSION_SUFFIX):
            if fileformat == 'bgzip' and tempname.endswith('.gz'):
                if get_preferred_gz_api() != 'bgzip':
                    continue
            if tempname.endswith(COMPRESSION_SUFFIX[fileformat]):
                return fileformat
    return None



def split_compression_suffix(filename):
    fileformat = infer_compression_format_by_suffix(filename)
    if fileformat is None:
        return filename, None
    else:
        return split_suffix(filename, COMPRESSION_SUFFIX[fileformat])



def strip_compression_suffix(filename):
    filename, suffix = split_compression_suffix(filename)
    return filename
