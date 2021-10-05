The Network Protocol Tool (npt)
=================================

Overview
--------

 The source code contained in the `npt` directory is broadly split into three
 categories:

  - input parsers (`parser_*.py`), that take a protocol described in a
    given format, and generate the intermediate representation;

  - helper classes (`rfc.py`, `protocol.py`, `util.py`, and `helpers.py`), that are used to
    construct and inspect the intermediate representation; and

  - output formatters (`formatter_*.py`), that take the intermediate
    representation, and produce output in a given format.

 Additionally, there is a directory of examples (`/examples`), containing a
 number of protocol definitions in each of the input parsers, and a helper
 script that performs the end-to-end process of
 taking a protocol description, and generating output in a specified format.

 Getting started
 ---------------

 The project uses Pipenv for dependency management. To begin, run:

 ```~~~~~~~~
 pipenv install --dev -e .
 ```

 to create a Python virtual environment with appropriate packages installed,
 and the npt tool installed in editable mode ready for development.
 Then, run:
 ```~~~~~~~~
 pipenv shell
 ```
 to start the virtual environment, within which you can run the scripts.

 To run the project's test suite, run:
 ```~~~~~~~~
 pipenv run tests
 ```

 Generating a protocol description
 ---------------------------------

 npt can be executed as follows:

```
python npt -d <output-dir> -of <output-format> <document>
```

where:

 * <document> is the name of the document to be processed. This is either
   a local filename, an RFC name, or an internet-draft name.

 * **-d** *output_dir*, **--dir** *output_dir* is the directory in which
   to place results


 * **-f** *formats*, **--outformat** *formats* :
    List of outputs to generate from parsing the draft/rfc specification.
    *formats* is a comma separated string.
    In generating the output, the script performs a depth-first search of the
    intermediate representation, to determine the order in which the necessary
    functions of the specified formatter are called.

    Currently supported output formats are :
    - *simple*  : a textual representation of the parsed IETF specification
    - *rust* : a rust protocol parser.

                        formats are simple,rust
 ```

*Example Usage*
```
   python npt -d foo -f simple examples/draft-mcquistin-quic-augmented-diagrams-03.xml 
   python npt -d foo -f simple examples/draft-mcquistin-augmented-ascii-diagrams-07.xml 
   python npt -d foo -f rust examples/draft-mcquistin-augmented-udp-example-00.xml 
   python npt -d foo -f rust examples/draft-mcquistin-augmented-tcp-example-00.xml 
```

## Acknowledgements

This work is funded by the UK Engineering and Physical Sciences Research
Council, under grant EP/R04144X/1. See [more information about the project](https://github.com/glasgow-ipl/ips-protodesc-code/blob/master/FUNDING.md).
