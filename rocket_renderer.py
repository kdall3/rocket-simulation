import pygame

import geometry
from rocket_parts import *

def render(rocket, root, container, auto_zoom=True, zoom_multiplier=0.95, normal_line_width=2, selected_line_width=5):
    container_centre = geometry.get_box_centre(container)

    total_length = 0
    max_diameter = 0

    for part in rocket.parts:
        if is_body_part(part):
            total_length += part.length
        if isinstance(part, Fins):
            if part.parent.diameter + 2 * part.width > max_diameter:
                max_diameter = part.parent.diameter + 2 * part.width
        else:
            if part.diameter > max_diameter:
                max_diameter = part.diameter

    if auto_zoom:
        try:
            if total_length / container[2] > max_diameter / container[3]:
                zoom = zoom_multiplier * container[2] / total_length
            else:
                zoom = zoom_multiplier * container[3] / max_diameter
        except ZeroDivisionError:
            zoom = 1

    length_rendered = 0
    total_length = total_length * zoom

    for part in rocket.parts:
        if hasattr(part, 'render'):
            part.render(root=root, rocket=rocket, zoom=zoom, length_rendered=length_rendered, total_length=total_length, graphic_centre=container_centre, normal_line_width=normal_line_width, selected_line_width=selected_line_width)
            if isinstance(part, BodyTube) or isinstance(part, NoseCone):
                length_rendered += part.length * zoom