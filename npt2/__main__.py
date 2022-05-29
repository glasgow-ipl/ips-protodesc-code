# =================================================================================================
# Copyright (C) 2022 University of Glasgow
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

import argparse

from npt2.loader             import Loader
from npt2.cleanup_text_nodes import cleanup_text_nodes

def main():
    ap = argparse.ArgumentParser(description=f"Network Protocol Tool v2")
    #ap.add_argument("-d", dest="outdir", required=True,  help="directory for output files")
    #ap.add_argument("-f", dest="format",  required=True,  help="output format")
    ap.add_argument("-v", dest="verbose", action="store_true", help="verbose")
    ap.add_argument("document", help="document to process")
    args = ap.parse_args()

    if args.verbose:
        print("*** Network Protocol Tool v2")
        print("")

    doc = Loader(args.document).load(verbose=args.verbose)
    cleanup_text_nodes(doc, args.verbose)

    # Print out the documents
    for node in doc.root().children(recursive=True):
        print(f"# {node.tag()}", end="")
        for n, v in node.attributes().items():
            print(f' {n}="{v}"', end="")
        print("")
        if node.has_text():
            print(f'   "{node.text()}"')



if __name__ == "__main__":
    main()

