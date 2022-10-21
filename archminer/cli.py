# SPDX-FileCopyrightText: 2022-present Ben Companjen <ben@companjen.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later
import click
import pathlib
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal
from .layout import relative_coords

@click.group(chain=True, invoke_without_command=True)
@click.option('--out-file', '-o', type=click.Path(path_type=pathlib.Path))
@click.option('--from-page', type=int)
@click.option('--to-page', type=int)
@click.argument('in-file', type=click.Path(exists=True, file_okay=True, path_type=pathlib.Path))
def cli(in_file, out_file, from_page, to_page):
    """Mine the PDF!"""
    pass

@cli.result_callback()
def process(processors, in_file, out_file, from_page, to_page):
    if from_page is not None and from_page > 0:
        processors.append(_high_pass(from_page))
    if to_page is not None and to_page > 0:
        processors.append(_low_pass(to_page))
    if from_page is not None and to_page is not None and to_page < from_page:
        raise ValueError("to-page must be higher than from-page")
    iterator = (_wrap_page_in_dict(page) for page in extract_pages(in_file))
    for processor in processors:
        iterator = processor(iterator)
    if out_file is None:
        out_file = in_file.with_suffix('.txt')

    with out_file.open('w') as out_fh:
        for page_dict in iterator:
            out_fh.write(page_dict["output"])
            page_layout = page_dict["page"]
            abs_bottoms = []
            rel_bottoms = []
            for element in page_layout:
                if isinstance(element, LTTextBoxHorizontal):
                    rel_left, rel_bottom, rel_width, rel_height = relative_coords(element.bbox, page_layout.bbox)
                    abs_bottoms.append(element.bbox[1])
                    rel_bottoms.append(rel_bottom)
                    if rel_bottom >= 0.87 or rel_bottom <= 0.095:
                        out_fh.write(element.get_text() + " ")
                        out_fh.write(str(element.bbox) + " ")
                        out_fh.write(str(relative_coords(element.bbox, page_layout.bbox)) + "\n")
            if len(abs_bottoms) == 0:
                continue
            out_fh.write(f'hi: {max(abs_bottoms)}/{max(rel_bottoms)}, lo: {min(abs_bottoms)}/{min(rel_bottoms)}\n')
            out_fh.write(f'hi - lo: {max(abs_bottoms) - min(abs_bottoms)}\n')

@cli.command('page-num')
def write_page_numbers():
    """Write page numbers in the output."""
    def page_number_writer(iterator):
        for page_dict in iterator:
            page_dict["output"] += f'---{page_dict["page"].pageid}---\n'
            yield page_dict
    return page_number_writer

def _high_pass(start_page: int):
    """Return an iterator that only returns pages starting at start page."""
    def page_filter(iterator):
        for page_dict in iterator:
            if page_dict["page"].pageid >= start_page:
                yield page_dict
    return page_filter

def _low_pass(end_page: int):
    """Return an iterator that stops the iteration at the given end page."""
    def page_filter(iterator):
        for page_dict in iterator:
            if page_dict["page"].pageid > end_page:
                return
            yield page_dict
    return page_filter

def _wrap_page_in_dict(page):
    return {"page": page, "output": ""}

if __name__ == "__main__":
    main()
