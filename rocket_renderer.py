import geometry
from rocket_parts import *

# Render a frame of the rocket pointed to the right
def render_rocket_editor(rocket, root, container, font=None, auto_zoom=True, zoom_multiplier=0.95, normal_line_width=2, selected_line_width=5, show_stages=False):
    container_centre = geometry.get_box_centre(container)

    total_length = 0
    max_diameter = 0

    for part in rocket.parts:
        if check_part_type(part, [BodyTube, NoseCone, Decoupler]):
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
        if not hasattr(part, 'render'):
            continue

        part.render(root=root, rocket=rocket, zoom=zoom, length_rendered=length_rendered, total_length=total_length, graphic_centre=container_centre, normal_line_width=normal_line_width, selected_line_width=selected_line_width)
        
        if show_stages and font is not None:
            current_part_stage = None
            for stage_number, stage_ids in enumerate(rocket.stages):
                if part.local_part_id in stage_ids:
                    current_part_stage = stage_number

            if current_part_stage is not None:
                stage_number_surface = font.render(str(current_part_stage), True, (255, 255, 255))
                part_middle = geometry.get_centroid_poly(part.hit_box)

                text_rect = stage_number_surface.get_rect(center = part_middle)

                root.blit(stage_number_surface, text_rect)
        if check_part_type(part, [BodyTube, NoseCone, Decoupler]):
            length_rendered += part.length * zoom


def render_rocket_simulation(current_rocket, original_rocket, flight_data, time_step, root, container, zoom_multiplier=0.95, line_width=2):  # time_step is how many steps of the simulation have been rendered since the start of the data
    # ZOOM
    container_centre = geometry.get_box_centre(container)

    total_length = 0
    max_diameter = 0

    for part in rocket.parts:
        if check_part_type(part, [BodyTube, NoseCone, Decoupler]):
            total_length += part.length
        if isinstance(part, Fins):
            if part.parent.diameter + 2 * part.width > max_diameter:
                max_diameter = part.parent.diameter + 2 * part.width
        else:
            if part.diameter > max_diameter:
                max_diameter = part.diameter

    try:
        zoom = zoom_multiplier * min(container[3:4]) / max([total_length, max_diameter])
    except ZeroDivisionError:
        zoom = 1
    
    length_rendered = 0
    
    # SIMULATION
    for part in current_rocket:
        if not hasattr(part, 'render'):
            continue

        if check_part_type(part, Engine):
            if part.get_stage(current_rocket) == flight_data['stage'][time_step]:
                part.render(root=root, rocket=current_rocket, zoom=zoom, length_rendered=length_rendered, total_length=total_length, graphic_centre=container_centre, normal_line_width=line_width, selected_line_width=line_width, burning=True, fuel=0.7)
        
        if check_part_type(part, [BodyTube, NoseCone, Decoupler]):
            length_rendered += part.length * zoom
