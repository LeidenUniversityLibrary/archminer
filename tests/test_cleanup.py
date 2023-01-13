# SPDX-FileCopyrightText: 2022 Leiden University Libraries <cds@library.leidenuniv.nl>
# SPDX-License-Identifier: GPL-3.0-or-later
import pytest
from archminer.cleanup import remove_breaks

@pytest.fixture
def text_with_breaks():
    return """
ALEGORÍA 

"""

@pytest.fixture
def file_with_breaks():
    with open("./tests/fixtures/paragraphs_bad.txt", encoding="utf-8") as f:
        return f.read()

@pytest.fixture
def file_without_breaks():
    with open("./tests/fixtures/paragraphs_good.txt", encoding="utf-8") as f:
        return f.read()

def test_remove_breaks(text_with_breaks):
    cleaned = remove_breaks(text_with_breaks)
    assert "ALEGORÍA" in cleaned
    assert len(cleaned.split("\n")) == 4

def test_remove_breaks_file(file_with_breaks, file_without_breaks):
    cleaned = remove_breaks(file_with_breaks)
    assert cleaned == file_without_breaks
