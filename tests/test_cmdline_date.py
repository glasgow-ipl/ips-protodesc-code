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
from datetime import datetime, timedelta
import time
import sys 

class Test_Cmdline_Date(ut.TestCase):
    def setUp(self):
        # generate a temporary directory name
        # remove actual directory - tool should a
        self.rootdir = pathlib.Path(tempfile.mkdtemp())
        self.argv = ["npt_prog"]

    def test_default_start_date(self):
        self.argv += f"-d {self.rootdir}".split()
        ap_ns, opts = npt.util.parse_cmdline(arglist=self.argv)
        with npt.util.RootWorkingDir(root=opts.root_dir) as rwd:
            draft_fetch_date = rwd.prev_sync_time('draft', None)
            self.assertEqual(draft_fetch_date, datetime.fromisoformat(npt.util.epoch))
            rfc_fetch_date = rwd.prev_sync_time('rfc', None)
            self.assertEqual(rfc_fetch_date, datetime.fromisoformat(npt.util.epoch))

    def test_preexisting_start(self):
        draft_fetch_date = None
        rfc_fetch_date = None
        write_time = None 

        self.argv += f"-d {self.rootdir}".split()
        ap_ns, opts = npt.util.parse_cmdline(arglist=self.argv)
        with npt.util.RootWorkingDir(root=opts.root_dir) as rwd:
            rwd.update_sync_time('draft')
            rwd.update_sync_time('rfc')
            write_time = rwd.sync_time

        with npt.util.RootWorkingDir(root=opts.root_dir) as rwd:
            draft_fetch_date = rwd.prev_sync_time('draft', None)
            rfc_fetch_date = rwd.prev_sync_time('rfc', None)
            self.assertEqual( write_time.strftime("%Y-%m-%dT%H:%M:%S"), draft_fetch_date.strftime("%Y-%m-%dT%H:%M:%S"))
            self.assertEqual( write_time.strftime("%Y-%m-%dT%H:%M:%S"), rfc_fetch_date.strftime("%Y-%m-%dT%H:%M:%S"))

    def test_date_override(self):
        override = (datetime.utcnow() - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%S")

        self.argv += f"-d {self.rootdir}".split()
        ap_ns, opts = npt.util.parse_cmdline(arglist=self.argv)
        with npt.util.RootWorkingDir(root=opts.root_dir) as rwd:
            rwd.update_sync_time('draft')
            rwd.update_sync_time('rfc')

        # Check date provided on command-line for drafts overrides cache-directory date 
        arguments = self.argv + f"-nd {override}".split()
        ap_ns, opts = npt.util.parse_cmdline(arglist=self.argv)
        with npt.util.RootWorkingDir(root=opts.root_dir) as rwd:
            self.assertLess( rwd.prev_sync_time('draft', override), rwd.prev_sync_time('draft', None))

        # Check date provided on command-line for rfc overrides cache-directory date 
        arguments = self.argv + f"-nr {override}".split()
        ap_ns, opts = npt.util.parse_cmdline(arglist=self.argv)
        with npt.util.RootWorkingDir(root=opts.root_dir) as rwd:
            self.assertLess( rwd.prev_sync_time('rfc', override), rwd.prev_sync_time('rfc', None))

    def tearDown(self):
        if self.rootdir.exists():
            shutil.rmtree(self.rootdir)


if __name__ == '__main__':
    ut.main()
