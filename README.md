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

 npt can be executed in three modes using the following options :

 1. **All new IETF drafts** : **-nd** [*from*], **--newdraft** [*from*]
    *Fetch new drafts since the last time tool was executed*.
    Example invocation :
    ```
    python npt -d <root-dir> --newdraft [from]
    ```
    If *from* is specified, all new IETF Drafts submitted since time *from*
    will be downloaded and processed.
    If *from* is not specified, the tool checks for a `.sync` file
    within the *<root-dir>* and resolves the previous time that at which the tool
    downloaded drafts from the IETF archive.
    executed. If `.sync` does not exist in `root-dir`, all drafts since
    "1970-01-01 00:00:00" will be downloaded and processed.
    The date *from*  is specified with format `yyyy-mm-dd HH:MM:SS`.
    All times are in UTC.

    After all required files are downloaded, the `.sync` file
    within the *root-dir* will be created / updated to
    the current time.


2. **All new IETF RFCs** : **-nr** [*from*], **--newrfc** [*from*]
    *Fetch new RFCs since the last time tool was executed*.
    Example invocation :
    ```
    python npt -d <root-dir> --newrfc [from]
    ```
    If *from* is specified, all new IETF RFCs submitted since time *from*
    will be downloaded and processed.
    If *from* is not specified, the tool checks for a `.sync` file
    within the *<root-dir>* and resolves the previous time at which the tool
    downloaded RFCs from the RFC index.
    If `.sync` does not exist in `root-dir`, all RFCs since
    "1970-01-01T00:00:00" will be downloaded and processed.
    The date *from*  is specified with format `yyyy-mm-ddTHH:MM:SS`.
    All times are in UTC.

    After all identified RFCs are downloaded, the `.sync` file
    within the *root-dir* will be created / updated to
    the current time.

 2. **Specified local files and/or IETF Drafts/RFCs** :
    Download specified IETF drafts/RFCs (if required), parse and generate parsers.
    Example invocation :

    ```
    python npt -d <root-dir>  draftname-[rev][.extn] rfcname[.extn] local-file
    ```
    Resolution of the input source occurs in the following order :
    * If the document is provided as a local file-path and the file exists,
       it is analysed and the output is placed in an `output` directory in the same
       directory that the input file is placed in.
       Both absolute and relative file-paths are supported.
    * If it is not a local input resource,
      1. If resource is an RFC name, query the RFC index and download the relevant RFC.
         If *extn* is specified along with the *rfcname*, download only specified extension
         if it is supported by the tool. Currently only "**.xml**" and "**.txt**"
         extensions are supported.
      2. If resource is a draft name, query the IETF data tracker and download the relevant draft(s).
         If *rev* is specified, download only the relevant revision of the draft.
         Otherwise download all revisions of the specfied draft-name.
         If *extn* is specified along with the *draftname*, download only specified extension
         if it is supported by the tool. Currently only "**.xml**" and "**.txt**"
         extensions are supported.


 Each of the tool's three modes can take the following options :
 1. **-d** *rootdir*, **--dir** *rootdir*  :
    All downloaded documents are stored under *rootdir*.
    If *rootdir* is specified and does not exist, a new directory will be created.
    If *rootdir* is not specified, the script will generate
    the default directory *ietf-data-cache* in the current working directory.
    The tool will generate the following file schema within the specified directory.

    ```
    rootdir
    |---- .sync
    │---- draft
    |     |---- <draft-name>/<rev>/<draft-name>-<rev>.xml
    |     |---- <draft-name>/<rev>/<draft-name>-<rev>.txt
    │---- rfc
    |     |--- <rfc-name>/<rfc-name>.xml
    |     |--- <rfc-name>/<rfc-name>.txt
    |---- output
    |     |---- draft
    |     |     |---- <draft-name>/<rev>/<draft-name>-<rev>.txt
    |     |     |---- <draft-name>/<rev>/<draft-name>-<rev>.rs
    |     |---- rfc
    |     |     |---- <rfc-name>/<rfc-name>.txt
    |     |     |---- <rfc-name>/<rfc-name>.rs
    ```

 2. **-of** *formats*, **--outformat** *formats* :
    List of outputs to generate from parsing the draft/rfc specification.
    *formats* is a comma separated string.
    In generating the output, the script performs a depth-first search of the
    intermediate representation, to determine the order in which the necessary
    functions of the specified formatter are called.

    Currently supported output formats are :
    - *simple*  : a textual representation of the parsed IETF specification
    - *rust* : a rust protocol parser.


 3. **-f**, **--force** :
    The default behaviour is to download a particular IETF *Draft/RFC* only
    if it has not already been downloaded.
    If the **-f**,**--force** flag is specified to over-ride this
    behaviour, an input file is downloaded and will over-write a pre-existing file.


 *Command usage*




 ```
 python npt [-h | --help ]
            [-nd | --newdraft [from]]
            [-nr [from]]
            [-d dir]
            [-of format]
            [-f]
            [uri [uri ...]]


 positional arguments:
  uri                   Provide draft/rfc/filenames. If name exists as a file,
                        treat it as a local file. If not search ietf
                        datatracker / rfc-index and download file. If a file-
                        extension is specified only that particular file-type
                        is downloaded. Otherwise all file types that can be
                        parsed are downloaded. If a revision is specified for
                        drafts, only that revision will downloaded. Otherwise
                        all revisions will be downloaded. draft format :
                        draft[-rev][.extn].rfc format : rfc[.extn]

optional arguments:
  -h, --help            show this help message and exit

  -nd [from], --newdraft [from]
                        Get all new drafts from ietf data tracker. If from
                        date is provided, pick up drafts from given date (fmt
                        'yyyy-mm-dd hh:mm:ss').
  -nr [from], --newrfc [from]
                        Get all new rfcs from ietf data tracker. If from date
                        is provided, pick up drafts from given date (fmt
                        'yyyy-mm-dd hh:mm:ss').
  -d dir, --dir dir     Root directory for all files. If given directory does
                        not exist, a new one will be created. Defaults to
                        ietf_data_cache within current working directory
  -of format, --outformat format
                        comma delimited list of output formats. Current output
                        formats are simple,rust
  -f, --force           Downloaded files will overwrite files in data
                        directory

 ```

*Example Usage*
```
   python npt examples/draft-mcquistin-quic-augmented-diagrams.xml -of simple
   python npt examples/draft-mcquistin-augmented-ascii-diagrams.xml -of simple
```

## Acknowledgements

This work is funded by the UK Engineering and Physical Sciences Research
Council, under grant EP/R04144X/1. See [more information about the project](https://github.com/glasgow-ipl/ips-protodesc-code/blob/master/FUNDING.md).
