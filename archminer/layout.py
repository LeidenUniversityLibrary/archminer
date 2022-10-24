# SPDX-FileCopyrightText: 2022 Leiden University Libraries <beheer@library.leidenuniv.nl>
# SPDX-License-Identifier: GPL-3.0-or-later

def relative_coords(bbox, page_bbox):
    """Return a tuple of coordinates relative to the page size."""
    page_width = page_bbox[2]
    page_height = page_bbox[3]
    return (
        round(bbox[0] / page_width, 3),
        round(bbox[1] / page_height, 3),
        round((bbox[2]-bbox[0]) / page_width, 3),
        round((bbox[3]-bbox[1]) / page_height, 3)
    )

def column_order(boxes, page_bbox):
    """Sort text boxes in column order.

    This works for text divided in two columns."""
    left_boxes = []
    right_boxes = []
    for box in boxes:
        if box.bbox[2] < page_bbox[2] / 2:
            left_boxes.append(box)
        else:
            right_boxes.append(box)
    return left_boxes + right_boxes
