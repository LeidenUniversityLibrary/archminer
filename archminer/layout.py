# SPDX-FileCopyrightText: 2022 Leiden University Libraries <beheer@library.leidenuniv.nl>
# SPDX-License-Identifier: GPL-3.0-or-later
import logging
LOG = logging.getLogger(__package__).getChild('layout')
LOG.info("Init child logger")
from shapely.geometry.polygon import Polygon
from shapely.geometry import MultiPolygon, box

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
    last_y_l, last_y_r = page_bbox[3], page_bbox[3]
    LOG.debug(f'Last Y: {last_y_l}')
    page_middle = page_bbox[2] / 2
    for box in boxes:
        w, h = round(box.bbox[2] - box.bbox[0], 2), round(box.bbox[3] - box.bbox[1], 2)
        box_center = (box.bbox[2] + box.bbox[0])/2
        if box_center < page_middle:
            left_boxes.append(box)
            LOG.debug(f"L {box.bbox} ({w}, {h})")
            if box.bbox[3] > last_y_l:
                LOG.warn(f"box out of vertical order: {box.bbox} > {last_y_l}")
            else:
                last_y_l = box.bbox[3]
        else:
            right_boxes.append(box)
            LOG.debug(f"R {box.bbox} ({w}, {h})")
            if box.bbox[3] > last_y_r:
                LOG.warn(f"box out of vertical order: {box.bbox} > {last_y_r}")
            else:
                last_y_r = box.bbox[3]
    return left_boxes + right_boxes

def detect_overlap(boxes) -> bool:
    """Detect whether boxes overlap."""
    polygons = []
    for box_ in boxes:
        b = box_.bbox
        p = box(b[0], b[1], b[2], b[3])
        polygons.append(p)
    mp = MultiPolygon(polygons)
    if not mp.is_valid:
        LOG.warn("Overlapping boxes detected!")
    return mp.is_valid
