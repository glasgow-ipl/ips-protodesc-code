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
from ietfdata import datatracker, rfcindex
import sys


class Test_Cmdline(ut.TestCase):
    def test_use_existing_rootdir(self):
        rootdir = pathlib.Path(tempfile.mkdtemp())

        self.assertTrue(
            rootdir.exists(),
            msg=f"Test harness error : Testing pre-existing Root Data Directory"
        )

        argv = f"-d {str(rootdir)}".split()
        ap_ns, opts = npt.util.parse_cmdline(arglist=argv)
        self.assertIsInstance(
            opts.root_dir,
            pathlib.Path,
            msg=f"generated dir - {opts.root_dir} is not of type pathlib.Path")
        self.assertEqual(
            rootdir,
            opts.root_dir,
            msg=f"Unexpected rootdir {opts.root_dir}. Expected {rootdir}")

        if rootdir.exists():
            shutil.rmtree(rootdir)

    def test_default_rootdir(self):
        current = pathlib.Path.cwd() / "ietf_data_cache"

        ap_ns, opts = npt.util.parse_cmdline(arglist=[])
        self.assertIsInstance(
            opts.root_dir,
            pathlib.Path,
            msg=f"generated dir - {opts.root_dir} is not of type pathlib.Path")
        self.assertEqual(
            opts.root_dir,
            current,
            msg=f"Unexpected rootdir {opts.root_dir}. Expected {current}")

        if current.exists():
            shutil.rmtree(current)

    def test_autogen_rootdir(self):
        rootdir = pathlib.Path(tempfile.mkdtemp())
        if rootdir.exists():
            rootdir.rmdir()

        argv = f"-d {rootdir}".split()
        ap_ns, opts = npt.util.parse_cmdline(arglist=argv)
        self.assertIsInstance(
            opts.root_dir,
            pathlib.Path,
            msg=f"generated dir - {opts.root_dir} is not of type pathlib.Path")
        self.assertEqual(
            opts.root_dir,
            rootdir,
            msg=f"Unexpected rootdir {opts.root_dir}. Expected {rootdir}")

        if rootdir.exists():
            shutil.rmtree(rootdir)

    def test_dir_structure(self):
        rootdir = pathlib.Path(tempfile.mkdtemp())
        argv = f"-d {rootdir}".split()
        ap_ns, opts = npt.util.parse_cmdline(arglist=argv)
        with npt.util.RootWorkingDir(root=opts.root_dir) as rwd:
            self.assertIsInstance(
                rwd.root,
                pathlib.Path,
                msg=
                f"root cache dir type {type(rwd.root)} is not a pathlib.Path instance"
            )
            self.assertTrue(rwd.root.exists(),
                            msg=f"Directory {rwd.root} not created")
            self.assertTrue(rwd.root.is_dir(),
                            msg=f"Filesys entry {rwd.root} is not a directory")

            # check whether .sync file exists
            rwd.update_sync_time("draft")  # force sync-file writing
            self.assertIsInstance(
                rwd.sync,
                pathlib.Path,
                msg=
                f"root .sync file {type(rwd.sync)} is not a pathlib.Path instance"
            )
            self.assertTrue(rwd.sync.exists(),
                            msg=f"Sync file {rwd.sync} missing")
            self.assertTrue(rwd.sync.is_file(),
                            msg=f"Sync file {rwd.sync} is not a regular file")

            # check whether input draft directory exists
            self.assertIsInstance(
                rwd.draft,
                pathlib.Path,
                msg=
                f"input draft {type(rwd.draft)} is not a pathlib.Path instance"
            )
            self.assertTrue(rwd.draft.exists(),
                            msg=f"Draft dir {rwd.draft} missing")
            self.assertTrue(rwd.draft.is_dir(),
                            msg=f"Draft dir {rwd.draft} is not dir")

            # check whether input rfc directory exists
            self.assertIsInstance(
                rwd.rfc,
                pathlib.Path,
                msg=
                f"RFC input dir {type(rwd.rfc)} is not a pathlib.Path instance"
            )
            self.assertTrue(rwd.rfc.exists(),
                            msg=f"RFC input dir {rwd.rfc} missing")
            self.assertTrue(rwd.rfc.is_dir(),
                            msg=f"RFC input dir {rwd.rfc} is not dir")

            # check whether output draft directory exists
            self.assertIsInstance(
                rwd.draft_out,
                pathlib.Path,
                msg=
                f"Draft output dir {type(rwd.draft_out)} is not a pathlib.Path instance"
            )
            self.assertTrue(rwd.draft_out.exists(),
                            msg=f"Draft output dir {rwd.draft_out} missing")
            self.assertTrue(rwd.draft_out.is_dir(),
                            msg=f"Draft output dir {rwd.draft_out} is not dir")

            # check whether output rfc directory exists
            self.assertIsInstance(
                rwd.rfc_out,
                pathlib.Path,
                msg=
                f"RFC output dir {type(rwd.rfc_out)} is not a pathlib.Path instance"
            )
            self.assertTrue(rwd.rfc_out.exists(),
                            msg=f"RFC output dir {rwd.rfc_out} missing")
            self.assertTrue(rwd.rfc_out.is_dir(),
                            msg=f"RFC output dir {rwd.rfc_out} is not dir")

        if rootdir.exists():
            shutil.rmtree(rootdir)

    def test_default_start_date(self):
        rootdir = pathlib.Path(tempfile.mkdtemp())
        argv = f"-d {str(rootdir)}".split()

        ap_ns, opts = npt.util.parse_cmdline(arglist=argv)
        with npt.util.RootWorkingDir(root=opts.root_dir) as rwd:
            draft_fetch_date = rwd.prev_sync_time('draft', None)
            self.assertEqual(draft_fetch_date,
                             datetime.fromisoformat(npt.util.epoch))
            rfc_fetch_date = rwd.prev_sync_time('rfc', None)
            self.assertEqual(rfc_fetch_date,
                             datetime.fromisoformat(npt.util.epoch))

        if rootdir.exists():
            shutil.rmtree(rootdir)

    def test_preexisting_start(self):
        rootdir = pathlib.Path(tempfile.mkdtemp())
        argv = f"-d {str(rootdir)}".split()

        ap_ns, opts = npt.util.parse_cmdline(arglist=argv)
        with npt.util.RootWorkingDir(root=opts.root_dir) as rwd:
            rwd.update_sync_time('draft')
            rwd.update_sync_time('rfc')
            write_time = rwd.sync_time

        with npt.util.RootWorkingDir(root=opts.root_dir) as rwd:
            draft_fetch_date = rwd.prev_sync_time('draft', None)
            rfc_fetch_date = rwd.prev_sync_time('rfc', None)
            self.assertEqual(write_time.isoformat(timespec="seconds"),
                             draft_fetch_date.isoformat(timespec="seconds"))
            self.assertEqual(write_time.isoformat(timespec="seconds"),
                             rfc_fetch_date.isoformat(timespec="seconds"))

        if rootdir.exists():
            shutil.rmtree(rootdir)

    def test_date_override(self):
        rootdir = pathlib.Path(tempfile.mkdtemp())
        argv = f"-d {str(rootdir)}".split()

        override = (datetime.utcnow() -
                    timedelta(days=10)).isoformat(timespec="seconds")

        ap_ns, opts = npt.util.parse_cmdline(arglist=argv)
        with npt.util.RootWorkingDir(root=opts.root_dir) as rwd:
            rwd.update_sync_time('draft')
            rwd.update_sync_time('rfc')

        # Check date provided on command-line for drafts overrides cache-directory date
        arguments = argv + f"-nd {override}".split()
        ap_ns, opts = npt.util.parse_cmdline(arglist=argv)
        with npt.util.RootWorkingDir(root=opts.root_dir) as rwd:
            self.assertLess(rwd.prev_sync_time('draft', override),
                            rwd.prev_sync_time('draft', None))

        # Check date provided on command-line for rfc overrides cache-directory date
        arguments = argv + f"-nr {override}".split()
        ap_ns, opts = npt.util.parse_cmdline(arglist=argv)
        with npt.util.RootWorkingDir(root=opts.root_dir) as rwd:
            self.assertLess(rwd.prev_sync_time('rfc', override),
                            rwd.prev_sync_time('rfc', None))

        if rootdir.exists():
            shutil.rmtree(rootdir)

    def test_dload_specific_draft(self):
        rootdir = pathlib.Path(tempfile.mkdtemp())
        draft_name = 'draft-mcquistin-augmented-ascii-diagrams-06.xml'
        argv = f"-d {str(rootdir)} {draft_name}".split()

        opts = npt.util.read_usr_opts(argv)
        self.assertIsInstance(opts.infiles[0].infile, pathlib.Path)
        self.assertTrue(opts.infiles[0].infile.exists())
        self.assertEqual(
            opts.infiles[0].infile.parent, rootdir / "draft" /
            "draft-mcquistin-augmented-ascii-diagrams" / "06")
        self.assertEqual(opts.infiles[0].infile.suffix, '.xml')

        if rootdir.exists():
            shutil.rmtree(rootdir)

    def test_dload_multiple_drafts(self):
        rootdir = pathlib.Path(tempfile.mkdtemp())
        draft_name = "draft-mcquistin-augmented-ascii-diagrams-06.xml draft-mcquistin-quic-augmented-diagrams-02.xml"
        argv = f"-d {str(rootdir)} {draft_name}".split()

        opts = npt.util.read_usr_opts(argv)
        for f in opts.infiles:
            self.assertIsInstance(f.infile, pathlib.Path)
            self.assertTrue(f.infile.exists())
            self.assertIn(f.name, draft_name)

            self.assertEqual(
                f.infile.parent, rootdir / "draft" / '-'.join(
                    (f.infile.stem.split(sep='-')[:-1])) /
                f.infile.stem.split(sep='-')[-1])
            self.assertEqual(f.infile.suffix, '.xml')

        if rootdir.exists():
            shutil.rmtree(rootdir)

    def test_dload_single_draft_allversions(self):
        rootdir = pathlib.Path(tempfile.mkdtemp())
        draft_name = 'draft-mcquistin-augmented-ascii-diagrams'
        argv = f"-d {str(rootdir)} {draft_name}".split()

        dt = datatracker.DataTracker()
        draft = dt.document_from_draft(draft_name)
        self.assertIsNotNone(draft)
        files = []
        for uri in draft.submissions:
            submission = dt.submission(uri)
            self.assertIsNotNone(submission)
            files += [
                pathlib.Path(_url).name for _ext, _url in submission.urls()
                if _ext in ['.xml', '.txt']
            ]

        opts = npt.util.read_usr_opts(argv)
        for d in [pathlib.Path(_f) for _f in files]:
            name, rev = '-'.join(
                d.stem.split(sep='-')[:-1]), d.stem.split(sep='-')[-1]
            _dl_file = rootdir / "draft" / name / rev / d
            self.assertTrue(_dl_file.exists(),
                            msg=f"{_dl_file} does not exist")
            self.assertTrue(_dl_file.is_file(),
                            msg=f"{_dl_file} is not a file")

        if rootdir.exists():
            shutil.rmtree(rootdir)

    def test_mutliple_local_files( self ):
        rootdir = pathlib.Path(tempfile.mkdtemp())
        draft_orig = [ 'draft-mcquistin-augmented-ascii-diagrams.xml', 'draft-mcquistin-quic-augmented-diagrams.xml' ]
        drafts = [ shutil.copy( pathlib.Path.cwd()/ "examples"/ in_file , rootdir ) for in_file in draft_orig ]
        argv = " ".join( drafts ).split()

        formats = ["simple", "rust"] 
        opts = npt.util.read_usr_opts(argv)

        for _file in opts.infiles : 
            for _fmt in formats : 
                outdir = rootdir / "output" / "draft" / _file.name / _fmt 
                self.assertEqual( outdir , _file.gen_filepath_out(opts.root_dir, _fmt ))

        if rootdir.exists():
            shutil.rmtree(rootdir)

if __name__ == '__main__':
    ut.main()
