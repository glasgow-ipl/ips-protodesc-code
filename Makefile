# Copyright (C) 2020 University of Glasgow
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

.PHONY: test typecheck unittests integrationtests

test: typecheck unittests integrationtests 

typecheck:
	mypy npt/*.py tests/*.py --junit-xml test-results/typecheck.xml

unittests:
	@python3 -m unittest discover -s tests/ -v

examples/output/%/rust: examples/%.xml
	npt $< -of rust

integrationtests: examples/output/draft-mcquistin-augmented-ascii-diagrams/rust examples/output/draft-mcquistin-quic-augmented-diagrams/rust
	cd examples/output/draft-mcquistin-augmented-ascii-diagrams/rust/draft-mcquistin-augmented-ascii-diagrams && cargo build
	cd examples/output/draft-mcquistin-quic-augmented-diagrams/rust/draft-mcquistin-quic-augmented-diagrams   && cargo build