# =================================================================================================
# Copyright (C) 2018-2021 University of Glasgow
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# SPDX-License-Identifier: BSD-2-Clause
# =================================================================================================

import pathlib
import tempfile
import shutil
import subprocess
import sys
import unittest

from datetime import datetime, timedelta
from ietfdata import datatracker, rfcindex
from pathlib  import Path


# The goal of these tests is to demonstrate that the command line options
# work. They test that appropriate files and directories are created, but
# don't check the contents of the created files.
class Test_Cmdline(unittest.TestCase):
    def test_cmdline_rust_mkdir(self):
        # Can we create an output directory?
        tmpdir = Path(tempfile.mkdtemp(prefix="test_cmdline"))
        subdir = tmpdir / "output"
        cargo_file  = subdir / "Cargo.toml"
        parser_dir  = subdir / "src"
        parser_file = parser_dir / "lib.rs"
        subprocess.run(["python", "-m", "npt", "-d", subdir, "-f", "rust", "draft-mcquistin-augmented-ascii-diagrams-07.xml"])
        self.assertTrue(subdir.is_dir())
        self.assertTrue(cargo_file.is_file())
        self.assertTrue(parser_dir.is_dir())
        self.assertTrue(parser_file.is_file())
        parser_file.unlink()
        parser_dir.rmdir()
        cargo_file.unlink()
        subdir.rmdir()
        tmpdir.rmdir()


    def test_cmdline_rust(self):
        # Can we use a pre-existing output directory? Same as test_cmdline_outdir_create, 
        # except that we create the output dir rather than letting the tool do so for us.
        tmpdir = Path(tempfile.mkdtemp(prefix="test_cmdline"))
        subdir = tmpdir / "output"
        subdir.mkdir()  # Create the output directory
        cargo_file  = subdir / "Cargo.toml"
        parser_dir  = subdir / "src"
        parser_file = parser_dir / "lib.rs"
        subprocess.run(["python", "-m", "npt", "-d", subdir, "-f", "rust", "draft-mcquistin-augmented-ascii-diagrams-07.xml"])
        self.assertTrue(subdir.is_dir())
        self.assertTrue(cargo_file.is_file())
        self.assertTrue(parser_dir.is_dir())
        self.assertTrue(parser_file.is_file())
        parser_file.unlink()
        parser_dir.rmdir()
        cargo_file.unlink()
        subdir.rmdir()
        tmpdir.rmdir()


    def test_cmdline_simple(self):
        # Can we use a pre-existing output directory? Same as test_cmdline_outdir_create, 
        # except that we create the output dir rather than letting the tool do so for us.
        tmpdir = Path(tempfile.mkdtemp(prefix="test_cmdline"))
        subdir = tmpdir / "output"
        subdir.mkdir()  # Create the output directory
        descr_file  = subdir / "description.txt"
        subprocess.run(["python", "-m", "npt", "-d", subdir, "-f", "simple", "draft-mcquistin-augmented-ascii-diagrams-07.xml"])
        self.assertTrue(subdir.is_dir())
        self.assertTrue(descr_file.is_file())
        descr_file.unlink()
        subdir.rmdir()
        tmpdir.rmdir()


if __name__ == '__main__':
    unittest.main()

