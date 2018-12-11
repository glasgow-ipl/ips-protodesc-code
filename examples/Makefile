define build
    pipenv run python ../parse-protodesc.py --input-format $(1) --input-file $(1)/$(2).$(3) --output-format c_parser --output-file $(1)/$(2).c --json-output-file $(1)/$(2).json
endef

all: textdesc extended_diagrams

textdesc: textdesc/*.json
textdesc/%.json: textdesc/%.def
	$(call build,'textdesc','example','def')
	$(call build,'textdesc','example_desc','def')
	$(call build,'textdesc','quic','def')
	$(call build,'textdesc','rtp','def')
	$(call build,'textdesc','tcp','def')
	$(call build,'textdesc','udp','def')
	$(call build,'textdesc','test','def')

extended_diagrams: extended_diagrams/*.json
extended_diagrams/%.json: extended_diagrams/%.txt
	$(call build,'extended_diagrams','rtcp','txt')
	$(call build,'extended_diagrams','rtp','txt')
	$(call build,'extended_diagrams','tcp','txt')
	$(call build,'extended_diagrams','udp','txt')

clean:
	rm **/*.json
	rm **/*.c
