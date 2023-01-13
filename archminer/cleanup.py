# SPDX-FileCopyrightText: 2022 Leiden University Libraries <cds@library.leidenuniv.nl>
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
LOG = logging.getLogger(__package__).getChild('cleanup')

def remove_breaks(text: str) -> str:
    """Remove line breaks within paragraphs."""
    r = []
    for line in text.split("\n"):
        r.append(line)
    return "\n".join(r)

def starts_block(line: str) -> bool:
    l = line.strip()
    if l.isupper():
        return True
    elif l.startswith("►"):
        return True
