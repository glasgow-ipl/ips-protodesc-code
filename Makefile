#
# Copyright (C) 2020-2022 University of Glasgow
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
# =================================================================================================
# Configuration for make:

# Warn if the Makefile references undefined variables and remove built-in rules:
MAKEFLAGS += --output-sync --warn-undefined-variables --no-builtin-rules --no-builtin-variables

# Remove output of failed commands, to avoid confusing later runs of make:
.DELETE_ON_ERROR:

# Remove obsolete old-style default suffix rules:
.SUFFIXES:

.PHONY: all pipenv-active test test-v2 unit-tests integration-tests clean


all: test test-v2

pipenv-active:
	@if [ ! $$PIPENV_ACTIVE ]; then echo "Activate pipenv before running make"; exit 1; fi


# =================================================================================================
# Test suite for `npt` library:

PYTHON_SRC   = $(wildcard npt/*.py)
PYTHON_TESTS = $(wildcard tests/*.py)

test: pipenv-active unit-tests integration-tests

# -------------------------------------------------------------------------------------------------
# Unit tests

test-results:
	mkdir $@

test-results/typecheck.xml: $(PYTHON_SRC) $(PYTHON_TESTS) | test-results
	@echo "*** Type checking: npt"
	@mypy npt/*.py tests/*.py --junit-xml test-results/typecheck.xml

unit-tests: test-results/typecheck.xml
	@echo "*** Running tests: npt"
	@python3 -m unittest discover -s tests/ -v

# -------------------------------------------------------------------------------------------------
# Integration tests

# This rule uses a grouped explicit target (an "&:" rule), so needs GNU make v4.3 or later.
test-results/%/Cargo.toml test-results/%/src/lib.rs &: examples/%.xml $(PYTHON_SRC)
	python -m npt -f rust -d $(dir $@) $<

tests/udp-testing/pcaps:
	mkdir  $@

tests/udp-testing/pcaps/%.pcap: tests/udp-testing/generate-pcap-%.py | tests/udp-testing/pcaps
	python $<

tests/tcp-testing/pcaps:
	mkdir  $@

tests/tcp-testing/pcaps/%.pcap: tests/tcp-testing/generate-pcap-%.py | tests/tcp-testing/pcaps
	python $<

tests/793bis-testing/pcaps:
	mkdir  $@

tests/793bis-testing/pcaps/%.pcap: tests/793bis-testing/generate-pcap-%.py | tests/793bis-testing/pcaps
	python $<
	
tests/rfc9293-testing/pcaps:
	mkdir  $@
	
tests/rfc9293-testing/pcaps/%.pcap: tests/rfc9293-testing/generate-pcap-%.py | tests/rfc9293-testing/pcaps
	python $<

integration-tests: tests/udp-testing/pcaps/udp-valid-1.pcap \
                   tests/udp-testing/pcaps/udp-invalid-badlength.pcap \
                   tests/tcp-testing/pcaps/tcp-ten-packets.pcap \
                   tests/793bis-testing/pcaps/tcp-ten-packets.pcap \
				   tests/rfc9293-testing/pcaps/tcp-ten-packets.pcap \
                   test-results/draft-mcquistin-augmented-udp-example-00/Cargo.toml \
                   test-results/draft-mcquistin-augmented-tcp-example-02/Cargo.toml \
                   test-results/draft-ietf-tcpm-rfc793bis-27/Cargo.toml \
				   test-results/rfc9293/Cargo.toml \
                   test-results/draft-mcquistin-augmented-ascii-diagrams-07/Cargo.toml
	cd tests/udp-testing/testharness && cargo test
	cd tests/tcp-testing/testharness && cargo test
	cd tests/793bis-testing/testharness && cargo test
	cd tests/rfc9293-testing/testharness && cargo test

# =================================================================================================
# Tests suite for `npt2` library

test-v2: pipenv-active
	@echo "*** Type checking: npt2"
	@mypy npt2/*.py tests-npt2/*.py
	@echo "*** Running tests: npt2"
	@python3 -m unittest discover -s tests-npt2/ -v

# =================================================================================================

clean:
	rm -f  test-results/typecheck.xml
	rm -f  tests/udp-testing/pcaps/udp-invalid-badlength.pcap
	rm -f  tests/udp-testing/pcaps/udp-valid-1.pcap
	rm -fr tests/udp-testing/pcaps
	rm -f  tests/tcp-testing/pcaps/tcp-ten-packets.pcap
	rm -fr tests/tcp-testing/pcaps
	rm -f  tests/793bis-testing/pcaps/tcp-ten-packets.pcap
	rm -fr tests/703bis-testing/pcaps
	rm -fr examples/output
	cd tests/udp-testing/testharness    && cargo clean
	cd tests/tcp-testing/testharness    && cargo clean
	cd tests/793bis-testing/testharness && cargo clean
	rm -fr test-results
	rm -fr build

