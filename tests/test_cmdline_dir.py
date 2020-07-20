# =================================================================================================
# Copyright (C) 2018-2020 University of Glasgow
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
import npt.util
import unittest as ut
import tempfile, shutil, pathlib
import time
import sys 


class Test_Cmdline_Dir(ut.TestCase):
    def setUp(self):
        # generate a temporary directory name
        # remove actual directory - tool should a
        self.rootdir = pathlib.Path(tempfile.mkdtemp())
        self.argv = ["npt_prog"]

    def test_use_existing_rootdir(self):
        self.assertTrue( self.rootdir.exists(),
            msg=f"Test harness error : Testing pre-existing Root Data Directory")

        self.argv += f"-d {str(self.rootdir)}".split()
        ap_ns, opts = npt.util.parse_cmdline( arglist=self.argv )
        self.assertIsInstance( opts.root_dir, pathlib.Path,
            msg=f"generated dir - {opts.root_dir} is not of type pathlib.Path")
        self.assertEqual( self.rootdir, opts.root_dir,
            msg=f"Unexpected rootdir {opts.root_dir}. Expected {self.rootdir}")

    def test_default_rootdir(self):
        current = pathlib.Path.cwd()
        ap_ns, opts = npt.util.parse_cmdline(arglist=self.argv)
        self.assertIsInstance( opts.root_dir, pathlib.Path,
            msg=f"generated dir - {opts.root_dir} is not of type pathlib.Path")
        self.assertEqual( opts.root_dir, current / "ietf_data_cache",
            msg=f"Unexpected rootdir {opts.root_dir}. Expected {self.rootdir}")

    def test_autogen_rootdir(self):
        if self.rootdir.exists():
            self.rootdir.rmdir()

        self.argv +=  f"-d {self.rootdir}".split()
        ap_ns, opts = npt.util.parse_cmdline(arglist=self.argv)
        self.assertIsInstance( opts.root_dir, pathlib.Path,
            msg=f"generated dir - {opts.root_dir} is not of type pathlib.Path")
        self.assertEqual( opts.root_dir, self.rootdir,
            msg=f"Unexpected rootdir {opts.root_dir}. Expected {self.rootdir}")

    def test_dir_structure(self):
        self.argv += f"-d {self.rootdir}".split()
        ap_ns, opts = npt.util.parse_cmdline(arglist=self.argv)
        with npt.util.RootWorkingDir(root=opts.root_dir) as rwd:
            self.assertIsInstance( rwd.root, pathlib.Path,
                msg= f"root cache dir type {type(rwd.root)} is not a pathlib.Path instance")
            self.assertTrue(rwd.root.exists(),
                            msg=f"Directory {rwd.root} not created")
            self.assertTrue(rwd.root.is_dir(),
                            msg=f"Filesys entry {rwd.root} is not a directory")

            # check whether .sync file exists
            rwd.update_sync_time("draft")   # force sync-file writing 
            self.assertIsInstance( rwd.sync, pathlib.Path, msg= f"root .sync file {type(rwd.sync)} is not a pathlib.Path instance")
            self.assertTrue(rwd.sync.exists(), msg=f"Sync file {rwd.sync} missing")
            self.assertTrue(rwd.sync.is_file(), msg=f"Sync file {rwd.sync} is not a regular file")

            # check whether input draft directory exists
            self.assertIsInstance( rwd.draft, pathlib.Path, msg= f"input draft {type(rwd.draft)} is not a pathlib.Path instance")
            self.assertTrue(rwd.draft.exists(), msg=f"Draft dir {rwd.draft} missing")
            self.assertTrue(rwd.draft.is_dir(), msg=f"Draft dir {rwd.draft} is not dir")

            # check whether input rfc directory exists
            self.assertIsInstance( rwd.rfc, pathlib.Path, msg= f"RFC input dir {type(rwd.rfc)} is not a pathlib.Path instance")
            self.assertTrue(rwd.rfc.exists(), msg=f"RFC input dir {rwd.rfc} missing")
            self.assertTrue(rwd.rfc.is_dir(), msg=f"RFC input dir {rwd.rfc} is not dir")

            # check whether output draft directory exists
            self.assertIsInstance( rwd.draft_out, pathlib.Path, msg= f"Draft output dir {type(rwd.draft_out)} is not a pathlib.Path instance")
            self.assertTrue(rwd.draft_out.exists(), msg=f"Draft output dir {rwd.draft_out} missing")
            self.assertTrue(rwd.draft_out.is_dir(), msg=f"Draft output dir {rwd.draft_out} is not dir")

            # check whether output rfc directory exists
            self.assertIsInstance( rwd.rfc_out, pathlib.Path, msg= f"RFC output dir {type(rwd.rfc_out)} is not a pathlib.Path instance")
            self.assertTrue(rwd.rfc_out.exists(), msg=f"RFC output dir {rwd.rfc_out} missing")
            self.assertTrue(rwd.rfc_out.is_dir(), msg=f"RFC output dir {rwd.rfc_out} is not dir")


    def tearDown(self):
        if self.rootdir.exists():
            shutil.rmtree(self.rootdir)

if __name__ == '__main__':
    ut.main()
