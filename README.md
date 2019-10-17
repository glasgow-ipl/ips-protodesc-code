Overview
--------

 The source code contained in this directory is broadly split into three
 categories:

  - input parsers (`/parsers`), that take a protocol described in a
    given format, and generate the intermediate representation;

  - a helper class (`protocol.py`), that is used to
    construct and inspect the intermediate representation; and

  - output formatters (`/formatters`), that take the intermediate
    representation, and produce output in a given format.

 Additionally, there is a directory of examples (`/examples`), containing a
 number of protocol definitions in each of the input parsers, and a helper
 script (`parse-ietf-doc.py`) that performs the end-to-end process of
 taking a protocol description, and generating output in a specified format.

 Getting started
 ---------------

 The project uses Pipenv for dependency management. To begin, run:

 ```~~~~~~~~
 pipenv install --dev
 ```

to create a Python virtual environment with appropriate packages install.
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

 The `parse-ietf-doc.py` script takes a protocol standards document,
 generates the intermediary representation, and produces
 output.

 *Command usage*

 ```
 python parse-ietf-doc.py --docname       <input document name>
                          --output-format <output format name>
                          --output-file   <output filename>
 ```

 In generating the output, the script performs a depth-first search of the
 intermediate representation, to determine the order in which the necessary
 functions of the specified formatter are called.

 The available output formats are:
  - simple_formatter (`txt`)
  - rust_formatter (`rs`)

  If `output-format` is not specified, the output format will be inferred from
  the file type specified as `output-file`. The file extensions that map to each
  output formatter are specified above.
