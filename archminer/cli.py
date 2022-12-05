# SPDX-FileCopyrightText: 2022-present Ben Companjen <ben@companjen.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later
import click
import pathlib
import logging
logging.getLogger('pdfminer').addHandler(logging.NullHandler())
LOG = logging.getLogger(__package__)
LOG.setLevel(logging.INFO)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
LOG.addHandler(ch)

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal, LAParams
from .layout import column_order


@click.group(chain=True, invoke_without_command=True)
@click.option('--out-file', '-o', type=click.Path(path_type=pathlib.Path))
@click.option('--from-page', type=int)
@click.option('--to-page', type=int)
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.argument('in-file', type=click.Path(exists=True, file_okay=True, path_type=pathlib.Path))
def cli(in_file, out_file, from_page, to_page, verbose):
    """Mine the PDF!"""
    pass

@cli.result_callback()
def process(processors, in_file, out_file, from_page, to_page, verbose):
    if verbose:
        LOG.setLevel(logging.DEBUG)
    if from_page is not None and from_page > 0:
        processors.append(_high_pass(from_page))
    if to_page is not None and to_page > 0:
        processors.append(_low_pass(to_page))
    if from_page is not None and to_page is not None and to_page < from_page:
        raise ValueError("to-page must be higher than from-page")
    la_params = LAParams(boxes_flow=None)
    iterator = (_wrap_page_in_dict(page) for page in extract_pages(in_file, laparams=la_params))
    for processor in processors:
        iterator = processor(iterator)
    if out_file is None:
        out_file = in_file.with_suffix('.txt')
    with out_file.open('w') as out_fh:
        for page_dict in iterator:
            out_fh.write(page_dict["output"])

@cli.command('page-num')
def write_page_numbers():
    """Write page numbers in the output."""
    def page_number_writer(iterator):
        for page_dict in iterator:
            page_dict["output"] += f'---{page_dict["page"].pageid}---\n'
            yield page_dict
    return page_number_writer

@cli.command('top-bottom')
def find_top_bottom_elements():
    """Record y coordinates for top and bottom elements."""
    def y_finder(iterator):
        for page_dict in iterator:
            page_layout = page_dict["page"]
            abs_bottoms = []
            text_boxes = []
            for element in page_layout:
                if isinstance(element, LTTextBoxHorizontal):
                    abs_bottoms.append(element.bbox[1])
                    text_boxes.append(element)
            page_dict["ordered_texts"] = column_order(text_boxes, page_layout.bbox)
            if len(abs_bottoms) > 0:
                page_dict["min_bottom"] = min(abs_bottoms)
                page_dict["max_bottom"] = max(abs_bottoms)
                # page_dict["output"] += f'hi: {max(abs_bottoms)}, lo: {min(abs_bottoms)}\n'
                # page_dict["output"] += f'hi - lo: {max(abs_bottoms) - min(abs_bottoms)}\n'
            yield page_dict
    return y_finder

@cli.command('remove-top-bottom')
def element_filter():
    """Write texts except the elements that are at the top or bottom.

    This requires that in a previous step the top and bottom elements' y coordinates
    were recorded."""
    def top_bottom_remover(iterator):
        for page_dict in iterator:
            if "min_bottom" in page_dict:
                if "ordered_texts" in page_dict:
                    for text_box in page_dict["ordered_texts"]:
                        # Add all text whose boundaries are between the bottom and top elements
                        if page_dict["min_bottom"] < text_box.bbox[1] and text_box.bbox[3] < page_dict["max_bottom"]:
                            page_dict["output"] += text_box.get_text() + "\n"
                else:
                    for element in page_dict["page"]:
                        if isinstance(element, LTTextBoxHorizontal):
                            # Add all text whose boundaries are between the bottom and top elements
                            if page_dict["min_bottom"] < element.bbox[1] and element.bbox[3] < page_dict["max_bottom"]:
                                page_dict["output"] += element.get_text() + "\n"
            yield page_dict
    return top_bottom_remover

def _high_pass(start_page: int):
    """Return an iterator that only returns pages starting at start page."""
    def page_filter(iterator):
        for page_dict in iterator:
            if page_dict["page"].pageid >= start_page:
                LOG.debug(f"Processing page {page_dict['page'].pageid}")
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
