#!/usr/bin/env python3

import os
import sys
import io
import gzip
import lzma
import locale
import unittest
import subprocess
import shutil

# Detect full paths for external executables used in stdio tests
# Prefer sys.executable for the Python interpreter, fallback to 'python3'
PY3 = sys.executable or shutil.which('python3') or 'python3'
# Find cat executable; if not present, fallback to /bin/cat or just 'cat'
CAT = shutil.which('cat') or '/bin/cat' or 'cat'

_PYTHON_VERSION = sys.version_info[:2]

if _PYTHON_VERSION < (3, 3):
    try:
        import bz2file as bz2  # type: ignore
    except ImportError:
        import bz2
else:
    import bz2

try:
    # optional; tests using bgzip will be skipped if missing
    # import may fail if pysam is not installed
    import bgzip
except Exception:
    bgzip = None

if sys.version_info < (3, 14):
    from backports import zstd
else:
    from compression import zstd

    

from compression import open, STDIO
from compression import is_stream, infer_encoding
# Additional unit tests for is_stream() and infer_encoding()

BEDLINE = "chr\t0\t1"


class CompressionTests(unittest.TestCase):
    def setUp(self):
        self.files = []

    def tearDown(self):
        for fn in list(self.files):
            try:
                os.remove(fn)
            except FileNotFoundError:
                pass

    def _write_file(self, filename, compression_arg):
        with open(filename, mode="w", compression=compression_arg) as o:
            print(BEDLINE, file=o)
        self.files.append(filename)

    def _read_first_line(self, filename, compression_arg=None):
        with open(filename, mode="r", compression=compression_arg) as i:
            return next(i).strip()

    # Caller tests (explicit)
    def test_0_caller_none_bed(self):
        fn = "test.caller.none.bed"
        self._write_file(fn, None)
        self.assertEqual(self._read_first_line(fn, None), BEDLINE)

    def test_0_caller_none_bed_gz(self):
        fn = "test.caller.none.bed.gz"
        # force gzip (avoid importing bgzip/pysam in test environment)
        self._write_file(fn, "gzip")
        self.assertEqual(self._read_first_line(fn, "gzip"), BEDLINE)

    def test_0_caller_none_bed_bz2(self):
        fn = "test.caller.none.bed.bz2"
        self._write_file(fn, None)
        self.assertEqual(self._read_first_line(fn, None), BEDLINE)

    def test_0_caller_none_bed_xz(self):
        fn = "test.caller.none.bed.xz"
        self._write_file(fn, None)
        self.assertEqual(self._read_first_line(fn, None), BEDLINE)

    def test_0_caller_io_bare(self):
        fn = "test.caller.io-bare.bed"
        self._write_file(fn, io)
        self.assertEqual(self._read_first_line(fn, io), BEDLINE)

    def test_0_caller_io_str(self):
        fn = "test.caller.io-str.bed"
        self._write_file(fn, "io")
        self.assertEqual(self._read_first_line(fn, "io"), BEDLINE)

    def test_0_caller_gzip_bare(self):
        fn = "test.caller.gzip-bare.bed"
        self._write_file(fn, gzip)
        self.assertEqual(self._read_first_line(fn, gzip), BEDLINE)

    def test_0_caller_gzip_str(self):
        fn = "test.caller.gzip-str.bed"
        self._write_file(fn, "gzip")
        self.assertEqual(self._read_first_line(fn, "gzip"), BEDLINE)

    def test_0_caller_bzip2_bare(self):
        fn = "test.caller.bzip2-bare.bed"
        self._write_file(fn, bz2)
        self.assertEqual(self._read_first_line(fn, bz2), BEDLINE)

    def test_0_caller_bzip2_str(self):
        fn = "test.caller.bzip2-str.bed"
        self._write_file(fn, "bz2")
        self.assertEqual(self._read_first_line(fn, "bz2"), BEDLINE)

    def test_0_caller_lzma_bare(self):
        fn = "test.caller.lzma-bare.bed"
        self._write_file(fn, lzma)
        self.assertEqual(self._read_first_line(fn, lzma), BEDLINE)

    def test_0_caller_lzma_str(self):
        fn = "test.caller.lzma-str.bed"
        self._write_file(fn, "lzma")
        self.assertEqual(self._read_first_line(fn, "lzma"), BEDLINE)

    def test_0_caller_xz_str(self):
        fn = "test.caller.xz-str.bed"
        self._write_file(fn, "xz")
        self.assertEqual(self._read_first_line(fn, "xz"), BEDLINE)

    def test_0_caller_zstd_bare(self):
        fn = "test.caller.zstd-bare.bed"
        self._write_file(fn, zstd)
        self.assertEqual(self._read_first_line(fn, zstd), BEDLINE)

    def test_0_caller_zstd_str(self):
        fn = "test.caller.zstd-str.bed"
        self._write_file(fn, "zstd")
        self.assertEqual(self._read_first_line(fn, "zstd"), BEDLINE)

    @unittest.skipIf(bgzip is None,"bgzip module not available")
    def test_0_caller_bgzip_bare(self):
        fn = "test.caller.bgzip-bare.bed"
        self._write_file(fn, bgzip)
        self.assertEqual(self._read_first_line(fn, bgzip), BEDLINE)
    
    @unittest.skipIf(bgzip is None,"bgzip module not available")
    def test_0_caller_bgzip_str(self):
        fn = "test.caller.bgzip-str.bed"
        self._write_file(fn, "bgzip")
        self.assertEqual(self._read_first_line(fn, "bgzip"), BEDLINE)

    # Stream tests (explicit)
    def test_1_stream_none(self):
        fn = "test.stream.none.bed"
        with open(fn, mode="w", compression=None) as o:
            print(BEDLINE, file=o)
        self.files.append(fn)
        self.assertEqual(self._read_first_line(fn, None), BEDLINE)

    def test_1_stream_io_bare(self):
        fn = "test.stream.io-bare.bed"
        with open(fn, mode="w", compression=io) as o:
            print(BEDLINE, file=o)
        self.files.append(fn)
        self.assertEqual(self._read_first_line(fn, io), BEDLINE)

    def test_1_stream_io_str(self):
        fn = "test.stream.io-str.bed"
        with open(fn, mode="w", compression="io") as o:
            print(BEDLINE, file=o)
        self.files.append(fn)
        self.assertEqual(self._read_first_line(fn, "io"), BEDLINE)

    def test_1_stream_gzip_bare(self):
        fn = "test.stream.gzip-bare.bed"
        with open(fn, mode="w", compression=gzip) as o:
            print(BEDLINE, file=o)
        self.files.append(fn)
        self.assertEqual(self._read_first_line(fn, gzip), BEDLINE)

    def test_1_stream_gzip_str(self):
        fn = "test.stream.gzip-str.bed"
        with open(fn, mode="w", compression="gzip") as o:
            print(BEDLINE, file=o)
        self.files.append(fn)
        self.assertEqual(self._read_first_line(fn, "gzip"), BEDLINE)

    def test_1_stream_bzip2_bare(self):
        fn = "test.stream.bzip2-bare.bed"
        with open(fn, mode="w", compression=bz2) as o:
            print(BEDLINE, file=o)
        self.files.append(fn)
        self.assertEqual(self._read_first_line(fn, bz2), BEDLINE)

    def test_1_stream_bzip2_str(self):
        fn = "test.stream.bzip2-str.bed"
        with open(fn, mode="w", compression="bz2") as o:
            print(BEDLINE, file=o)
        self.files.append(fn)
        self.assertEqual(self._read_first_line(fn, "bz2"), BEDLINE)

    def test_1_stream_lzma_bare(self):
        fn = "test.stream.lzma-bare.bed"
        with open(fn, mode="w", compression=lzma) as o:
            print(BEDLINE, file=o)
        self.files.append(fn)
        self.assertEqual(self._read_first_line(fn, lzma), BEDLINE)

    def test_1_stream_lzma_str(self):
        fn = "test.stream.lzma-str.bed"
        with open(fn, mode="w", compression="lzma") as o:
            print(BEDLINE, file=o)
        self.files.append(fn)
        self.assertEqual(self._read_first_line(fn, "lzma"), BEDLINE)

    def test_1_stream_xz_str(self):
        fn = "test.stream.xz-str.bed"
        with open(fn, mode="w", compression="xz") as o:
            print(BEDLINE, file=o)
        self.files.append(fn)
        self.assertEqual(self._read_first_line(fn, "xz"), BEDLINE)

    def test_1_stream_zstd_bare(self):
        fn = "test.stream.zstd-bare.bed"
        with open(fn, mode="w", compression=zstd) as o:
            print(BEDLINE, file=o)
        self.files.append(fn)
        self.assertEqual(self._read_first_line(fn, zstd), BEDLINE)

    def test_1_stream_zstd_str(self):
        fn = "test.stream.zstd-str.bed"
        with open(fn, mode="w", compression="zstd") as o:
            print(BEDLINE, file=o)
        self.files.append(fn)
        self.assertEqual(self._read_first_line(fn, "zstd"), BEDLINE)

    def test_1_stream_lzma_str(self):
        fn = "test.stream.lzma-str.bed"
        with open(fn, mode="w", compression="lzma") as o:
            print(BEDLINE, file=o)
        self.files.append(fn)
        self.assertEqual(self._read_first_line(fn, "lzma"), BEDLINE)

    @unittest.skipIf(bgzip is None,"bgzip module not available")
    def test_1_stream_bgzip_bare(self):
        fn = "test.stream.bgzip-bare.bed"
        with open(fn, mode="w", compression=bgzip) as o:
            print(BEDLINE, file=o)
        self.files.append(fn)
        self.assertEqual(self._read_first_line(fn, bgzip), BEDLINE)

    @unittest.skipIf(bgzip is None,"bgzip module not available")
    def test_1_stream_bgzip_str(self):
        fn = "test.stream.bgzip-str.bed"
        with open(fn, mode="w", compression="bgzip") as o:
            print(BEDLINE, file=o)
        self.files.append(fn)
        self.assertEqual(self._read_first_line(fn, "bgzip"), BEDLINE)

    # URL tests (explicit) — skip on network errors
    def test_2_url_none(self):
        url = "https://raw.githubusercontent.com/bredeson/compression/refs/heads/main/test/test.none.bed"
        try:
            with open(url, mode="r", compression=None) as i:
                line = next(i).strip()
        except Exception as e:
            self.skipTest("skipping URL test due to: {0}" % str(e))
        self.assertEqual(line, BEDLINE)

    def test_2_url_io(self):
        url = "https://raw.githubusercontent.com/bredeson/compression/refs/heads/main/test/test.io.bed"
        try:
            with open(url, mode="r", compression="io") as i:
                line = next(i).strip()
        except Exception as e:
            self.skipTest("skipping URL test due to: {0}" % str(e))
        self.assertEqual(line, BEDLINE)

    def test_2_url_gzip(self):
        url = "https://raw.githubusercontent.com/bredeson/compression/refs/heads/main/test/test.gzip.bed.gz"
        try:
            with open(url, mode="r", compression="gzip") as i:
                line = next(i).strip()
        except Exception as e:
            self.skipTest("skipping URL test due to: {0}" % str(e))
        self.assertEqual(line, BEDLINE)

    def test_2_url_bzip2(self):
        url = "https://raw.githubusercontent.com/bredeson/compression/refs/heads/main/test/test.bzip2.bed.bz2"
        try:
            with open(url, mode="r", compression="bz2") as i:
                line = next(i).strip()
        except Exception as e:
            self.skipTest("skipping URL test due to: {0}" % str(e))
        self.assertEqual(line, BEDLINE)

    def test_2_url_lzma(self):
        url = "https://raw.githubusercontent.com/bredeson/compression/refs/heads/main/test/test.lzma.bed.xz"
        try:
            with open(url, mode="r", compression="lzma") as i:
                line = next(i).strip()
        except Exception as e:
            self.skipTest("skipping URL test due to: {0}" % str(e))
        self.assertEqual(line, BEDLINE)

    def test_2_url_xz(self):
        url = "https://raw.githubusercontent.com/bredeson/compression/refs/heads/main/test/test.xz.bed.xz"
        try:
            with open(url, mode="r", compression="xz") as i:
                line = next(i).strip()
        except Exception as e:
            self.skipTest("skipping URL test due to: {0}" % str(e))
        self.assertEqual(line, BEDLINE)

    @unittest.skipIf(bgzip is None,"bgzip module not available")
    def test_0_url_bgzip(self):
        url = "https://raw.githubusercontent.com/bredeson/compression/refs/heads/main/test/test.bgzip.bed.gz"
        with open(url, mode="r", compression="bgzip") as i:
            line = next(i).strip()
        self.assertEqual(line, BEDLINE)

    # STDIO write tests (explicit)
    def test_3_stdio_write_none(self):
        script = "test.stdio.none.py"
        src = 'from compression import STDIO, open\nwith open(STDIO, mode="w", compression=None) as o:\n    print("chr\\t0\\t1", file=o)\n'
        out = "test.stdio.none.bed"
        with open(script, "w") as s:
            s.write(src)
        self.files.extend([script, out])
        subprocess.run("{PY3} {script} > {out}".format(PY3=PY3,script=script,out=out), shell=True, check=True)
        self.assertEqual(self._read_first_line(out, None), BEDLINE)

    def test_3_stdio_write_io_bare(self):
        script = "test.stdio.io-bare.py"
        src = 'import io\nfrom compression import STDIO, open\nwith open(STDIO, mode="w", compression=io) as o:\n    print("chr\\t0\\t1", file=o)\n'
        out = "test.stdio.io-bare.bed"
        with open(script, "w") as s:
            s.write(src)
        self.files.extend([script, out])
        subprocess.run("{PY3} {script} > {out}".format(PY3=PY3,script=script,out=out), shell=True, check=True)
        self.assertEqual(self._read_first_line(out, "io"), BEDLINE)

    def test_3_stdio_write_io_str(self):
        script = "test.stdio.io-str.py"
        src = 'from compression import STDIO, open\nwith open(STDIO, mode="w", compression=\"io\") as o:\n    print("chr\\t0\\t1", file=o)\n'
        out = "test.stdio.io-str.bed"
        with open(script, "w") as s:
            s.write(src)
        self.files.extend([script, out])
        subprocess.run("{PY3} {script} > {out}".format(PY3=PY3,script=script,out=out), shell=True, check=True)
        self.assertEqual(self._read_first_line(out, "io"), BEDLINE)

    def test_3_stdio_write_gzip_bare(self):
        script = "test.stdio.gzip-bare.py"
        src = 'import gzip\nfrom compression import STDIO, open\nwith open(STDIO, mode="w", compression=gzip) as o:\n    print("chr\\t0\\t1", file=o)\n'
        out = "test.stdio.gzip-bare.bed"
        with open(script, "w") as s:
            s.write(src)
        self.files.extend([script, out])
        subprocess.run("{PY3} {script} > {out}".format(PY3=PY3,script=script,out=out), shell=True, check=True)
        self.assertEqual(self._read_first_line(out, "gzip"), BEDLINE)

    def test_3_stdio_write_gzip_str(self):
        script = "test.stdio.gzip-str.py"
        src = 'from compression import STDIO, open\nwith open(STDIO, mode="w", compression=\"gzip\") as o:\n    print("chr\\t0\\t1", file=o)\n'
        out = "test.stdio.gzip-str.bed"
        with open(script, "w") as s:
            s.write(src)
        self.files.extend([script, out])
        subprocess.run("{PY3} {script} > {out}".format(PY3=PY3,script=script,out=out), shell=True, check=True)
        self.assertEqual(self._read_first_line(out, "gzip"), BEDLINE)

    def test_3_stdio_write_bzip2_bare(self):
        script = "test.stdio.bzip2-bare.py"
        src = 'import bz2\nfrom compression import STDIO, open\nwith open(STDIO, mode="w", compression=bz2) as o:\n    print("chr\\t0\\t1", file=o)\n'
        out = "test.stdio.bzip2-bare.bed"
        with open(script, "w") as s:
            s.write(src)
        self.files.extend([script, out])
        subprocess.run("{PY3} {script} > {out}".format(PY3=PY3,script=script,out=out), shell=True, check=True)
        self.assertEqual(self._read_first_line(out, "bz2"), BEDLINE)

    def test_3_stdio_write_bzip2_str(self):
        script = "test.stdio.bzip2-str.py"
        src = 'from compression import STDIO, open\nwith open(STDIO, mode="w", compression=\"bz2\") as o:\n    print("chr\\t0\\t1", file=o)\n'
        out = "test.stdio.bzip2-str.bed"
        with open(script, "w") as s:
            s.write(src)
        self.files.extend([script, out])
        subprocess.run("{PY3} {script} > {out}".format(PY3=PY3,script=script,out=out), shell=True, check=True)
        self.assertEqual(self._read_first_line(out, "bz2"), BEDLINE)

    def test_3_stdio_write_lzma_bare(self):
        script = "test.stdio.lzma-bare.py"
        src = 'import lzma\nfrom compression import STDIO, open\nwith open(STDIO, mode="w", compression=lzma) as o:\n    print("chr\\t0\\t1", file=o)\n'
        out = "test.stdio.lzma-bare.bed"
        with open(script, "w") as s:
            s.write(src)
        self.files.extend([script, out])
        subprocess.run("{PY3} {script} > {out}".format(PY3=PY3,script=script,out=out), shell=True, check=True)
        self.assertEqual(self._read_first_line(out, "lzma"), BEDLINE)

    def test_3_stdio_write_lzma_str(self):
        script = "test.stdio.lzma-str.py"
        src = 'from compression import STDIO, open\nwith open(STDIO, mode="w", compression=\"lzma\") as o:\n    print("chr\\t0\\t1", file=o)\n'
        out = "test.stdio.lzma-str.bed"
        with open(script, "w") as s:
            s.write(src)
        self.files.extend([script, out])
        subprocess.run("{PY3} {script} > {out}".format(PY3=PY3,script=script,out=out), shell=True, check=True)
        self.assertEqual(self._read_first_line(out, "lzma"), BEDLINE)

    def test_3_stdio_write_xz_str(self):
        script = "test.stdio.xz-str.py"
        src = 'from compression import STDIO, open\nwith open(STDIO, mode="w", compression=\"xz\") as o:\n    print("chr\\t0\\t1", file=o)\n'
        out = "test.stdio.xz-str.bed"
        with open(script, "w") as s:
            s.write(src)
        self.files.extend([script, out])
        subprocess.run("{PY3} {script} > {out}".format(PY3=PY3,script=script,out=out), shell=True, check=True)
        self.assertEqual(self._read_first_line(out, "xz"), BEDLINE)

    @unittest.skipIf(bgzip is None,"bgzip module not available")
    def test_3_stdio_write_bgzip_bare(self):
        script = "test.stdio.bgzip-bare.py"
        src = 'import bgzip\nfrom compression import STDIO, open\nwith open(STDIO, mode="w", compression=bgzip) as o:\n    print("chr\\t0\\t1", file=o)\n'
        out = "test.stdio.bgzip-bare.bed"
        with open(script, "w") as s:
            s.write(src)
        self.files.extend([script, out])
        subprocess.run("{PY3} {script} > {out}".format(PY3=PY3,script=script,out=out), shell=True, check=True)
        self.assertEqual(self._read_first_line(out, "bgzip"), BEDLINE)

    @unittest.skipIf(bgzip is None,"bgzip module not available")
    def test_3_stdio_write_bgzip_str(self):
        script = "test.stdio.bgzip-str.py"
        src = 'from compression import STDIO, open\nwith open(STDIO, mode="w", compression=\"bgzip\") as o:\n    print("chr\\t0\\t1", file=o)\n'
        out = "test.stdio.bgzip-str.bed"
        with open(script, "w") as s:
            s.write(src)
        self.files.extend([script, out])
        subprocess.run("{PY3} {script} > {out}".format(PY3=PY3,script=script,out=out), shell=True, check=True)
        self.assertEqual(self._read_first_line(out, "bgzip"), BEDLINE)

    # STDIO read tests (explicit)
    def test_4_stdio_read_none(self):
        script = "test.stdio.none.py"
        src = 'from compression import STDIO, open\nwith open(STDIO, mode="r", compression=None) as i:\n    l = next(i).strip()\n    assert l == "chr\\t0\\t1"\n'
        with open(script, "w") as s:
            s.write(src)
        self.files.append(script)
        # ensure input file exists for the read test
        infile = "test.stdio.none.bed"
        self._write_file(infile, None)
        # use absolute executable paths for robustness
        subprocess.run("{CAT} {infile} | {PY3} {script}".format(PY3=PY3,CAT=CAT,script=script,infile=infile), shell=True, check=True)

    def test_4_stdio_read_io_bare(self):
        script = "test.stdio.io-bare.py"
        src = 'import io\nfrom compression import STDIO, open\nwith open(STDIO, mode="r", compression=io) as i:\n    l = next(i).strip()\n    assert l == "chr\\t0\\t1"\n'
        with open(script, "w") as s:
            s.write(src)
        self.files.append(script)
        infile = "test.stdio.io-bare.bed"
        self._write_file(infile, io)
        subprocess.run("{CAT} {infile} | {PY3} {script}".format(PY3=PY3,CAT=CAT,script=script,infile=infile), shell=True, check=True)

    def test_4_stdio_read_io_str(self):
        script = "test.stdio.io-str.py"
        src = 'from compression import STDIO, open\nwith open(STDIO, mode="r", compression=\"io\") as i:\n    l = next(i).strip()\n    assert l == "chr\\t0\\t1"\n'
        with open(script, "w") as s:
            s.write(src)
        self.files.append(script)
        infile = "test.stdio.io-str.bed"
        self._write_file(infile, "io")
        subprocess.run("{CAT} {infile} | {PY3} {script}".format(PY3=PY3,CAT=CAT,script=script,infile=infile), shell=True, check=True)

    def test_4_stdio_read_gzip_bare(self):
        script = "test.stdio.gzip-bare.py"
        src = 'import gzip\nfrom compression import STDIO, open\nwith open(STDIO, mode="r", compression=gzip) as i:\n    l = next(i).strip()\n    assert l == "chr\\t0\\t1"\n'
        with open(script, "w") as s:
            s.write(src)
        self.files.append(script)
        infile = "test.stdio.gzip-bare.bed"
        self._write_file(infile, gzip)
        subprocess.run("{CAT} {infile} | {PY3} {script}".format(PY3=PY3,CAT=CAT,script=script,infile=infile), shell=True, check=True)

    def test_4_stdio_read_gzip_str(self):
        script = "test.stdio.gzip-str.py"
        src = 'from compression import STDIO, open\nwith open(STDIO, mode="r", compression=\"gzip\") as i:\n    l = next(i).strip()\n    assert l == "chr\\t0\\t1"\n'
        with open(script, "w") as s:
            s.write(src)
        self.files.append(script)
        infile = "test.stdio.gzip-str.bed"
        self._write_file(infile, "gzip")
        subprocess.run("{CAT} {infile} | {PY3} {script}".format(PY3=PY3,CAT=CAT,script=script,infile=infile), shell=True, check=True)

    def test_4_stdio_read_bzip2_bare(self):
        script = "test.stdio.bzip2-bare.py"
        src = 'import bz2\nfrom compression import STDIO, open\nwith open(STDIO, mode="r", compression=bz2) as i:\n    l = next(i).strip()\n    assert l == "chr\\t0\\t1"\n'
        with open(script, "w") as s:
            s.write(src)
        self.files.append(script)
        infile = "test.stdio.bzip2-bare.bed"
        self._write_file(infile, bz2)
        subprocess.run("{CAT} {infile} | {PY3} {script}".format(PY3=PY3,CAT=CAT,script=script,infile=infile), shell=True, check=True)

    def test_4_stdio_read_bzip2_str(self):
        script = "test.stdio.bzip2-str.py"
        src = 'from compression import STDIO, open\nwith open(STDIO, mode="r", compression=\"bz2\") as i:\n    l = next(i).strip()\n    assert l == "chr\\t0\\t1"\n'
        with open(script, "w") as s:
            s.write(src)
        self.files.append(script)
        infile = "test.stdio.bzip2-str.bed"
        self._write_file(infile, "bz2")
        subprocess.run("{CAT} {infile} | {PY3} {script}".format(PY3=PY3,CAT=CAT,script=script,infile=infile), shell=True, check=True)

    def test_4_stdio_read_lzma_bare(self):
        script = "test.stdio.lzma-bare.py"
        src = 'import lzma\nfrom compression import STDIO, open\nwith open(STDIO, mode="r", compression=lzma) as i:\n    l = next(i).strip()\n    assert l == "chr\\t0\\t1"\n'
        with open(script, "w") as s:
            s.write(src)
        self.files.append(script)
        infile = "test.stdio.lzma-bare.bed"
        self._write_file(infile, lzma)
        subprocess.run("{CAT} {infile} | {PY3} {script}".format(PY3=PY3,CAT=CAT,script=script,infile=infile), shell=True, check=True)

    def test_4_stdio_read_lzma_str(self):
        script = "test.stdio.lzma-str.py"
        src = 'from compression import STDIO, open\nwith open(STDIO, mode="r", compression=\"lzma\") as i:\n    l = next(i).strip()\n    assert l == "chr\\t0\\t1"\n'
        with open(script, "w") as s:
            s.write(src)
        self.files.append(script)
        infile = "test.stdio.lzma-str.bed"
        self._write_file(infile, "lzma")
        subprocess.run("{CAT} {infile} | {PY3} {script}".format(PY3=PY3,CAT=CAT,script=script,infile=infile), shell=True, check=True)

    def test_4_stdio_read_xz_str(self):
        script = "test.stdio.xz-str.py"
        src = 'from compression import STDIO, open\nwith open(STDIO, mode="r", compression=\"xz\") as i:\n    l = next(i).strip()\n    assert l == "chr\\t0\\t1"\n'
        with open(script, "w") as s:
            s.write(src)
        self.files.append(script)
        infile = "test.stdio.xz-str.bed"
        self._write_file(infile, "xz")
        subprocess.run("{CAT} {infile} | {PY3} {script}".format(PY3=PY3,CAT=CAT,script=script,infile=infile), shell=True, check=True)


class TestCompressionUtils(unittest.TestCase):
    def test_is_stream_true(self):
        class DummyStream:
            def __next__(self):
                return 1
            def close(self):
                pass
        stream = DummyStream()
        self.assertTrue(is_stream(stream))

    def test_is_stream_false_obj(self):
        class NotAStream:
            def close(self):
                pass
        obj = NotAStream()
        self.assertFalse(is_stream(obj))
    
    def test_is_stream_false_list(self):
        self.assertFalse(is_stream([]))

    def test_is_stream_false_string(self):
        self.assertFalse(is_stream("string"))


    def test_infer_encoding_none(self):
        # Should return preferred encoding
        expected = locale.getpreferredencoding(False)
        self.assertEqual(infer_encoding(None), expected)

    def test_infer_encoding_explicit(self):
        self.assertEqual(infer_encoding("utf-8"), "utf-8")
        self.assertEqual(infer_encoding("ascii"), "ascii")


if __name__ == "__main__":
    unittest.main()


