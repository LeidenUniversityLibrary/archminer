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
@click.argument('in-file', type=click.Path(exists=True, file_okay=True, path_type=pathlib.Path))
def cli(in_file, out_file):
    """Mine the PDF!"""
    pass

@cli.result_callback()
def process(processors, in_file, out_file):
    if out_file is None:
        out_file = in_file.with_suffix('.txt')

    with out_file.open('w') as out_fh:
        for page_num, page_layout in enumerate(extract_pages(in_file)):
            out_fh.write(f'---{page_num + 1}---\n')
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

if __name__ == "__main__":
    main()
