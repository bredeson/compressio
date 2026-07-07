# compressio

## About

Open a gzip-/bgzip-/bzip2-/lzma-/xz-compressed file or uncompressed file
in binary or text mode.

The `filename` argument can be an actual filename (a str or bytes object), or
an existing file object to read from or write to. Use `"-"` to open a file
object to the appropriate stdin/stdout stream requested via mode. Serial
readling via HTTP and FTP URL file path is supported.

The `mode` argument can be `"r"`, `"rb"`, `"w"`, `"wb"`, `"x"`, `"xb"`, `"a"` or
`"ab"` for binary mode, or `"rt"`, `"wt"`, `"xt"` or `"at"` for text mode. The
default mode is `"rt"`. The default `compresslevel` for compression streams is
9.

For binary mode, the `encoding`, `errors`, and `newline` arguments must not be
provided.

For text mode, a compressed stream object is created, then wrapped in an
`io.TextIOWrapper` instance with the specified encoding, error handling
behavior, and line ending(s).

To read from/write to compressed streams from stdin/stdout or existing
file-like objects, the appropriate compression algorithm name must must
passed via the `compression` argument (e.g., `compression=gzip`). When
writing `compresslevel` must be set to a value between 1 and 9, inclusive
(default is 9).

This module relies on the `io`, `gzip`, `lzma`, `bz2`, (optionally) `bz2file`, 
`pysam` and `zstd` modules internally, but others can be supplied via the 
`compression` argument, which must return an object with a callable `open()` 
method. The `bz2file` module is only required for Python versions earlier 
than 3.3. The `zstd` module is availble via the `backports` module prior to
Python 3.14 and the `compression` module thereafter.

See Also: `help(io.open)`


## Examples

```python3
from compressio import open

# open a file for reading on the local file system
# (algorithm 'gzip' is automatically detected):
infile = open("input.fastq.gz", mode='r')

# open a file for reading on a remote server via HTTP protocol
infile = open("http://path/to/remote/input.fastq.gz")

# open a file for reading (writing) to STDIN (STDOUT) stream. To read
# compressed files, must specify the `compression` attribute explicitly.
# Call one of the supported compression algorithms by name:
from compressio.constants import STDIO
infile = open(STDIO, mode='r', compression='gzip')

# or pass the module object directly:
import gzip
infile = open(STDIO, mode='r', compression=gzip)

outfile = open(STDIO, mode='w', compression=gzip)
```

## Limitations
The `bgzip` compression interface cannot read from (or write to) existing file
streams, and in such cases `gzip` is used. If this behavior is not desired,
please open the file stream directly via `compressio.open()` using the file
name.

Writing to files on remote servers has not been tested.

## Other dependencies

- **io**
- **locale**
- **os**
- **pysam** (required for bgzip compression)
- **sys**
- **urllib**
- **zstd**

