Overview
--------

 The source code contained in this directory is broadly split into three
 categories:

  - input parsers (`/input_parsers`), that take a protocol described in a
    given format, and generate the intermediate representation;

  - helper classes (`protocol.py` and `protocoltypes.py`), that are used to
    construct and inspect the intermediate representation; and

  - output formatters (`/formatters`), that take the intermediate
    representation, and produce output in a given format.

 Additionally, there is a directory of examples (`/examples`), containing a
 number of protocol definitions in each of the input parsers, and a helper
 script (`parse-protodesc.py`) that performs the end-to-end process of
 taking a protocol description, and generating output in a specified format.

 Getting started 
 ---------------
 
 The project uses Pipenv for dependency management. To begin, run:
 
 ```~~~~~~~~
 pipenv shell
 ```
 
 Generating a protocol description
 ---------------------------------
 
 The `parse-protodesc.py` script takes a protocol description, in a
 specified format, generates the intermediary representation, and produces
 output in a specified format. 

 *Command usage*
 
 ```
 python parse-protodesc.py --input-format      <input format name>
                           --input-file        <input filename>
                           --output-format     <output format name>
                           --output-file       <output filename>
 ```

 In generating the output, the script performs a depth-first search of the
 intermediate representation, to determine the order in which the necessary
 functions of the specified formatter are called. 

 The available input formats are: 
  - packetlang

 The available output formats are:
  - simpleprinter
