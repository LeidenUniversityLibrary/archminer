# archminer

[![PyPI - Version](https://img.shields.io/pypi/v/archminer.svg)](https://pypi.org/project/archminer)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/archminer.svg)](https://pypi.org/project/archminer)

-----

`archminer` is a command-line tool that extracts text from a specific PDF,
referred to as 'Marginados'.
The text in the Marginados PDF was created through OCR, as the PDF is a scan.
This tool tries to extract the text in reading order.

The tool makes assumptions specific to the Marginados PDF:

- only certain pages are relevant
- the text is layed out in two columns
- each (relevant) page has a header line and a page number in the footer line

**Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation

```console
pip install archminer
```

## Usage

As mentioned above, this tool has expectations about the input PDF.

It is expected that you use it like this:

```console
archminer --from-page 6 --to-page 590 Marginados_all.pdf top-bottom remove-top-bottom
```

This reads pages 6 through 590 from the PDF, determines the coordinates of the
top (header) and bottom (footer) lines, then removes those lines and writes the
text contents of the pages in reading order to *Marginados_all.txt* (because we
did not specify an output file).

See `archminer --help` for the full usage.

## License

`archminer` is distributed under the terms of the [GPLv3](https://spdx.org/licenses/GPL-3.0-or-later.html) license or any later version.
