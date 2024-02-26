import geometry
from rocket_parts import *

# Render a frame of the rocket pointed to the right
def render_rocket_editor(rocket, root, container, font=None, auto_zoom=True, zoom_multiplier=0.95, normal_line_width=2, selected_line_width=5, show_stages=False, angle=0):
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

        part.render(root=root, rocket=rocket, zoom=zoom, length_rendered=length_rendered, total_length=total_length, graphic_centre=container_centre, normal_line_width=normal_line_width, selected_line_width=selected_line_width, angle=angle)
        
        if check_part_type(part, [BodyTube, NoseCone, Decoupler]):
            length_rendered += part.length * zoom

        # Stage numbering
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


def render_rocket_simulation(current_rocket, flight_data, time_step, angle, root, container, font=None, zoom_multiplier=0.9, line_width=2, reference_line_separation=100):  # time_step is how many steps of the simulation have been rendered since the start of the data
    # ZOOM
    container_centre = geometry.get_box_centre(container)

    total_length = 0
    max_diameter = 0

    for part in current_rocket.parts:
        if check_part_type(part, [BodyTube, NoseCone, Decoupler]):
            total_length += part.length
        if isinstance(part, Fins):
            if part.parent.diameter + 2 * part.width > max_diameter:
                max_diameter = part.parent.diameter + 2 * part.width
        else:
            if part.diameter > max_diameter:
                max_diameter = part.diameter

    try:
        zoom = zoom_multiplier * min(container[2], container[3]) / max(total_length, max_diameter)
    except ZeroDivisionError:
        zoom = 1

    total_length = total_length * zoom

    length_rendered = 0

    # ROCKET
    for part in current_rocket.parts:
        if not hasattr(part, 'render'):
            continue

        if check_part_type(part, [Engine]):
            if part.get_stage(current_rocket) == flight_data['stage'][time_step-1]:  # Engine burning
                part.render(root=root, rocket=current_rocket, zoom=zoom, length_rendered=length_rendered, total_length=total_length, graphic_centre=container_centre, normal_line_width=line_width, selected_line_width=line_width, angle=angle, burning=True, fuel=flight_data["fuel"][time_step-1])
            else:  # Engine not burning
                part.render(root=root, rocket=current_rocket, zoom=zoom, length_rendered=length_rendered, total_length=total_length, graphic_centre=container_centre, normal_line_width=line_width, selected_line_width=line_width, angle=angle, burning=False, fuel=1)
        else:
            part.render(root=root, rocket=current_rocket, zoom=zoom, length_rendered=length_rendered, total_length=total_length, graphic_centre=container_centre, normal_line_width=line_width, selected_line_width=line_width, angle=angle)
        
        if check_part_type(part, [BodyTube, NoseCone, Decoupler]):
            length_rendered += part.length * zoom

    # ALTITUDE REFERENCE LINES
    current_altitude = flight_data['altitude'][time_step-1]
    altitude_line_width = math.ceil(6 * zoom_multiplier)  # Altitude lines get thinner as the camera zooms out to give the illusion of depth

    # Apoapsis line
    apoapsis = max(flight_data['altitude'])
    y_coord = (current_altitude - apoapsis) * zoom + container_centre[1]

    if container[1] + container[3] >= y_coord >= container[1]:
        pygame.draw.line(root, (150, 150, 150), (container[0], y_coord), (container[0] + container[2], y_coord), altitude_line_width)
        if font is not None:
            altitude_marker_surface = font.render('Apoapsis', True, (255, 255, 255))
            text_rect = altitude_marker_surface.get_rect(center=(container[0] + 50, y_coord))

            root.blit(altitude_marker_surface, text_rect)
    
    # Incremental altitude lines
    for line_altitude in range(0, int(max(flight_data['altitude'])), reference_line_separation):
        y_coord = (current_altitude - line_altitude) * zoom + container_centre[1]

        if container[1] + container[3] >= y_coord >= container[1]:
            pygame.draw.line(root, (100, 100, 100), (container[0], y_coord), (container[0] + container[2], y_coord), altitude_line_width)
            if font is not None:
                altitude_marker_surface = font.render(str(line_altitude), True, (255, 255, 255))
                text_rect = altitude_marker_surface.get_rect(center=(container[0] + 50, y_coord))

                root.blit(altitude_marker_surface, text_rect)


def draw_slider(root, start, end, position, colour=(255, 255, 255), line_width=3, button_radius=10):  # position should be 0 -> 1
    pygame.draw.line(root, colour, start, end, width=line_width)

    line_vector = geometry.get_distance_vector(start, end)
    circle_pos = [line_vector[0] * position + start[0], line_vector[1] * position + start[1]]

    pygame.draw.circle(root, colour, circle_pos, button_radius)

    return circle_pos
