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

PYTHON_SRC   = $(wildcard npt/*.py)
PYTHON_TESTS = $(wildcard tests/*.py)

UDP_GEN_PCAPS = tests/udp-testing/pcaps/udp-invalid-badlength.pcap \
				tests/udp-testing/pcaps/udp-valid-1.pcap

TCP_GEN_PCAPS = tests/tcp-testing/pcaps/ten_tcp_packets.pcap

793BIS_GEN_PCAPS = tests/793bis-testing/pcaps/ten_tcp_packets.pcap

.PHONY: test unittests integrationtests

test: unittests integrationtests

test-results/typecheck.xml: $(PYTHON_SRC) $(PYTHON_TESTS)
	mypy npt/*.py tests/*.py --junit-xml test-results/typecheck.xml

unittests: test-results/typecheck.xml $(PYTHON_SRC) $(PYTHON_TESTS)
	@python3 -m unittest discover -s tests/ -v

$(UDP_GEN_PCAPS): tests/udp-testing/generate-pcaps.py
	mkdir -p tests/udp-testing/pcaps
	cd tests/udp-testing && python generate-pcaps.py

$(TCP_GEN_PCAPS): tests/tcp-testing/generate-pcaps.py
	mkdir -p tests/tcp-testing/pcaps
	cd tests/tcp-testing && python generate-pcaps.py

$(793BIS_GEN_PCAPS): tests/793bis-testing/generate-pcaps.py
	mkdir -p tests/793bis-testing/pcaps
	cd tests/793bis-testing && python generate-pcaps.py

examples/output/draft/%/rust: examples/%.xml $(PYTHON_SRC)
	python3 -m npt $< -of rust

examples/output/draft/draft-ietf-tcpm-rfc793bis/25/rust:
	python3 -m npt draft-ietf-tcpm-rfc793bis-25 -d examples -of rust
	
integrationtests: $(UDP_GEN_PCAPS) $(TCP_GEN_PCAPS) $(793BIS_GEN_PCAPS) \
	              examples/output/draft/draft-mcquistin-augmented-udp-example-00/rust \
	              examples/output/draft/draft-mcquistin-augmented-tcp-example-00/rust \
				  examples/output/draft/draft-mcquistin-augmented-ascii-diagrams-07/rust \
				  examples/output/draft/draft-ietf-tcpm-rfc793bis/25/rust
	cd tests/udp-testing/testharness && cargo test
	cd tests/tcp-testing/testharness && cargo test
	cd tests/793bis-testing/testharness && cargo test

# =================================================================================================

clean:
	rm -rf $(UDP_GEN_PCAPS)
	rm -rf $(TCP_GEN_PCAPS)
	rm -rf $(793BIS_GEN_PCAPS)
	rm -f  test-results/typecheck.xml
	rm -fr examples/output
	cd tests/udp-testing/testharness    && cargo clean
	cd tests/tcp-testing/testharness    && cargo clean
	cd tests/793bis-testing/testharness && cargo clean

