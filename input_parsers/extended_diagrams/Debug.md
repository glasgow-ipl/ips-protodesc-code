```
python parse-protodesc.py --input-format extended_diagrams --input-file examples/extended_diagrams/tcp.txt --output-format c_parser --output-file examples/extended_diagrams/tcp.c --json-output-file examples/extended_diagrams/tcp.json
```

# Debug
To debug the extended diagrams input parser without relying on the rest of the project run the following command in the src/ directory:
```
python -m input_parsers.extended_diagrams <INPUT FILE>
```

E.g.
```
python -m input_parsers.extended_diagrams examples/extended_diagrams/tcp.txt
```

```
python parse-protodesc.py --input-format extended_diagrams --input-file examples/extended_diagrams/udp.txt --output-format c_parser --output-file examples/extended_diagrams/udp.c --json-output-file examples/extended_diagrams/udp.json
```
