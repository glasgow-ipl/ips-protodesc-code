from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name         = "npt",
    version      = "0.1.0",
    author       = "Colin Perkins",
    author_email = "csp@csperkins.org",
    description  = "Access the IETF Data Tracker and RFC Index",
    long_description = long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/glasgow-ipl/ips-protodesc-code",
    packages = ['npt'],
    package_data = {
        'npt': ['py.typed', 'grammar_rfc.txt' ],
    },
    entry_points = {
        'console_scripts': [
            'npt = npt.__main__:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7'
)

