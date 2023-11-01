import pygame
import math

import geometry


def check_part_type(part, part_whitelist):
        for whitelisted_part in part_whitelist:
            if isinstance(part, whitelisted_part):
                return True
        return False


def get_entry(master, variable, last_value, blacklist=[None, 0]):
    entry = master.part_editor_elements[f'{variable} entry'].get_text()
    try:
        if float(entry) not in blacklist:
            return float(master.part_editor_elements[f'{variable} entry'].get_text())
        else:
            return last_value
    except ValueError:
        return last_value


class RocketPart():
    def __init__(self, colour=(255, 255, 255), local_part_id=None):
        self.local_part_id = local_part_id

        self.colour = colour

        self.being_dragged = False
        self.selected = False
        self.mass_override = False

        self.hit_box = (0, 0, 0, 0)


class Rocket():
    def __init__(self, name='New Rocket', parts=[]):
        self.name = name
        self.parts = parts
        self.new_part_id = 0

        self.stages = [] # List of lists of part ids


class BodyTube(RocketPart):
    def __init__(self, length=1, diameter=0.3, wall_thickness=0.01, density=1330, mass=None, colour=(255, 255, 255), local_part_id=None):
        super().__init__(colour, local_part_id)

        self.length = length
        self.diameter = diameter
        self.wall_thickness = wall_thickness
        self.density = density
        self.mass = self.get_mass()

        
    def editor_update_variables(self, master):
        if self.selected:
            self.length = get_entry(master, 'length', self.length)
            self.diameter = get_entry(master, 'diameter', self.diameter)
            self.wall_thickness = get_entry(master, 'wall thickness', self.wall_thickness)
            self.density = get_entry(master, 'density', self.density)
            
            if not self.mass_override:
                self.mass = self.get_mass()
            else:
                self.mass = get_entry(master, 'mass', self.mass)
    
    def get_mass(self):
        return round(self.density * math.pi * self.length * (self.diameter**2 - (self.diameter - self.wall_thickness)**2) / 4, 10)
    
    def render(self, root, rocket, zoom, length_rendered, total_length, graphic_centre, normal_line_width, selected_line_width):
        if self.selected:
            line_width = selected_line_width
        else:
            line_width = normal_line_width
        
        if self.being_dragged:
            mouse_pos = pygame.mouse.get_pos()
            self.hit_box = (mouse_pos[0] - zoom*self.length/2, mouse_pos[1] - zoom*self.diameter/2, self.length*zoom, self.diameter*zoom)
            self.vertices = [(self.hit_box[0], self.hit_box[1]), (self.hit_box[0] + self.hit_box[2], self.hit_box[1]), 
                             (self.hit_box[0] + self.hit_box[2], self.hit_box[1] + self.hit_box[3]), (self.hit_box[0], self.hit_box[1] + self.hit_box[3])]

            pygame.draw.polygon(root, self.colour, self.vertices, line_width)
        else:
            start_x = graphic_centre[0] + length_rendered - total_length/2
            self.hit_box = (start_x, graphic_centre[1] - zoom*self.diameter/2, self.length*zoom, self.diameter*zoom)
            self.vertices = [(self.hit_box[0], self.hit_box[1]), (self.hit_box[0] + self.hit_box[2], self.hit_box[1]), 
                             (self.hit_box[0] + self.hit_box[2], self.hit_box[1] + self.hit_box[3]), (self.hit_box[0], self.hit_box[1] + self.hit_box[3])]

            pygame.draw.polygon(root, self.colour, self.vertices, line_width)


class NoseCone(RocketPart):
    def __init__(self, cone_shape='conic', length=0.3, diameter=0.3, density=1330, mass=None, colour=(255, 255, 255), local_part_id=None):
        super().__init__(colour, local_part_id)

        self.cone_shape = cone_shape
        self.length = length
        self.diameter = diameter
        self.density = density
        self.mass = self.get_mass()

    
    def editor_update_variables(self, master):
        if self.selected:
            self.length = get_entry(master, 'length', self.length)
            self.diameter = get_entry(master, 'diameter', self.diameter)
            
            if not self.mass_override:
                self.mass = self.get_mass()
            else:
                self.mass = get_entry(master, 'mass', self.mass)
    
    def get_mass(self):
        if self.cone_shape == 'conic':
            return round(math.pi * (self.diameter/2)**2 * self.length/3, 10)
        else:
            raise Exception('Invalid cone shape')

    def render(self, root, rocket, zoom, length_rendered, total_length, graphic_centre, normal_line_width, selected_line_width):
        if self.selected:
            line_width = selected_line_width
        else:
            line_width = normal_line_width

        if self.being_dragged:
            mouse_pos = pygame.mouse.get_pos()

            if self.cone_shape == 'conic':
                self.hit_box = (mouse_pos[0] - zoom*self.length/2, mouse_pos[1] - zoom*self.diameter/2, self.length*zoom, self.diameter*zoom)
                pygame.draw.polygon(root, self.colour, [(self.hit_box[0], mouse_pos[1]), (self.hit_box[0] + self.hit_box[2], self.hit_box[1]), 
                                                            (self.hit_box[0] + self.hit_box[2], self.hit_box[1] + self.hit_box[3])], line_width)
        else:
            if self.cone_shape == 'conic':
                start_x = graphic_centre[0] + length_rendered - total_length/2
                self.hit_box = (start_x, graphic_centre[1] - zoom*self.diameter/2, self.length*zoom, self.diameter*zoom)
                pygame.draw.polygon(root, self.colour, [(self.hit_box[0], graphic_centre[1]), (self.hit_box[0] + self.hit_box[2], self.hit_box[1]), 
                                                            (self.hit_box[0] + self.hit_box[2], self.hit_box[1] + self.hit_box[3])], line_width)


class Engine(RocketPart):
    def __init__(self, parent_id=None, length=0.5, diameter=0.1, mass=1, propellant_mass=0.9, offset=0, average_thrust=100, burn_time=10, colour=(255, 255, 255), local_part_id=None):
        super().__init__(colour, local_part_id)

        self.length = length
        self.diameter = diameter
        self.mass = mass
        self.propellant_mass = propellant_mass
        self.offset = offset
        self.average_thrust = average_thrust
        self.burn_time = burn_time

        self.parent_id = parent_id
        self.parent = BodyTube()  # Skeleton object to reference before update_variables is first called


    def editor_update_variables(self, master):
        for part in master.rocket.parts:
            if part.local_part_id == self.parent_id:
                self.parent = part

        if self.selected:
            self.length = get_entry(master, 'length', self.length)
            self.diameter = get_entry(master, 'diameter', self.diameter)
            self.offset = get_entry(master, 'offset', self.offset, blacklist=[None])
            self.average_thrust = get_entry(master, 'average thrust', self.average_thrust)
            self.burn_time = get_entry(master, 'burn time', self.burn_time)
            self.propellant_mass = get_entry(master, 'propellant mass', self.propellant_mass)
            
            if self.mass_override:
                self.mass = get_entry(master, 'mass', self.mass)
    
    def render(self, rocket, root, zoom, length_rendered, total_length, graphic_centre, normal_line_width, selected_line_width):
        for part in rocket.parts:
            if part.local_part_id == self.parent_id:
                self.parent = part

        if self.selected:
            line_width = selected_line_width
        else:
            line_width = normal_line_width

        if self.being_dragged:
            mouse_pos = pygame.mouse.get_pos()
            self.hit_box = (mouse_pos[0] - zoom*self.length/2, mouse_pos[1] - zoom*self.diameter/2, self.length*zoom, self.diameter*zoom)
            self.vertices = [(self.hit_box[0], self.hit_box[1]), (self.hit_box[0] + self.hit_box[2], self.hit_box[1]), 
                             (self.hit_box[0] + self.hit_box[2], self.hit_box[1] + self.hit_box[3]), (self.hit_box[0], self.hit_box[1] + self.hit_box[3])]

            pygame.draw.polygon(root, self.colour, self.vertices, line_width)
        else:
            parent_centre = geometry.get_box_centre(self.parent.hit_box)
            start_x = self.parent.hit_box[0] + self.parent.hit_box[2] + self.offset - self.length*zoom 
            start_y = parent_centre[1] - (self.diameter/2)*zoom
            self.hit_box = (start_x, start_y, self.length*zoom, self.diameter*zoom)
            self.vertices = [(self.hit_box[0], self.hit_box[1]), (self.hit_box[0] + self.hit_box[2], self.hit_box[1]), 
                             (self.hit_box[0] + self.hit_box[2], self.hit_box[1] + self.hit_box[3]), (self.hit_box[0], self.hit_box[1] + self.hit_box[3])]

            pygame.draw.polygon(root, self.colour, self.vertices, line_width)


class Fins(RocketPart):
    def __init__(self, parent_id=None, fin_shape='triangle', fin_count=4, length=0.2, thickness=0.05, width=0.1, offset=0, mass=1, colour=(255, 255, 255), local_part_id=None):
        super().__init__(colour, local_part_id)

        self.fin_shape = fin_shape
        self.fin_count = fin_count
        self.width = width
        self.length = length
        self.thickness = thickness
        self.offset = offset
        self.mass = mass

        self.parent_id = parent_id
        self.parent = BodyTube() # Skeleton object to reference before update_variables is first called

    
    def editor_update_variables(self, master):
        for part in master.rocket.parts:
            if part.local_part_id == self.parent_id:
                self.parent_id = part.local_part_id
                self.parent = part

        if self.selected:
            self.length = get_entry(master, 'length', self.length)
            self.width = get_entry(master, 'width', self.width)
            self.thickness = get_entry(master, 'thickness', self.thickness)
            self.offset = get_entry(master, 'offset', self.offset, blacklist=[None])

            if self.mass_override:
                self.mass = get_entry(master, 'mass', self.mass)
    
    def render(self, rocket, root, zoom, length_rendered, total_length, graphic_centre, normal_line_width, selected_line_width):
        for part in rocket.parts:
            if part.local_part_id == self.parent_id:
                self.parent = part
        
        if self.selected:
            line_width = selected_line_width
        else:
            line_width = normal_line_width
        
        if self.being_dragged:
            mouse_pos = pygame.mouse.get_pos()
            if self.fin_shape == 'triangle':
                start_x = mouse_pos[0] - (self.length/2)*zoom
                self.hit_box = [(start_x, mouse_pos[1] - self.parent.hit_box[3]/2 - self.width*zoom, self.length*zoom, self.width*zoom),
                              (start_x, mouse_pos[1] + self.parent.hit_box[3]/2, self.length*zoom, self.width*zoom)]
                pygame.draw.polygon(root, self.colour, [(self.hit_box[0][0], self.hit_box[0][1] + self.hit_box[0][3]), (self.hit_box[0][0] + self.hit_box[0][2], self.hit_box[0][1] + self.hit_box[0][3]),
                                                               (self.hit_box[0][0] + self.hit_box[0][2], self.hit_box[0][1])], line_width)
                pygame.draw.polygon(root, self.colour, [(self.hit_box[1][0], self.hit_box[1][1]), (self.hit_box[1][0] + self.hit_box[1][2], self.hit_box[1][1]),
                                                               (self.hit_box[1][0] + self.hit_box[1][2], self.hit_box[1][1] + self.hit_box[1][3])], line_width)
        else:
            if self.fin_shape == 'triangle':
                start_x = self.parent.hit_box[0] + self.parent.hit_box[2] + self.offset*zoom - self.length*zoom 
                self.hit_box = [(start_x, self.parent.hit_box[1]-self.width*zoom, self.length*zoom, self.width*zoom), 
                              (start_x, self.parent.hit_box[1]+self.parent.hit_box[3], self.length*zoom, self.width*zoom)]
                pygame.draw.polygon(root, self.colour, [(self.hit_box[0][0], self.parent.hit_box[1]), (self.hit_box[0][0] + self.hit_box[0][2], self.parent.hit_box[1]),
                                                               (self.hit_box[0][0] + self.hit_box[0][2], self.hit_box[0][1])], line_width)
                pygame.draw.polygon(root, self.colour, [(self.hit_box[1][0], self.hit_box[1][1]), (self.hit_box[1][0] + self.hit_box[1][2], self.hit_box[1][1]),
                                                               (self.hit_box[1][0] + self.hit_box[1][2], self.hit_box[1][1] + self.hit_box[1][3])], line_width)


class Decoupler(RocketPart):
    def __init__(self, length=0.05, diameter=0.3, mass=0.1, colour=(255, 255, 255), local_part_id=None):
        super().__init__(colour, local_part_id)

        self.length = length
        self.diameter = diameter
        self.mass = mass
    
    def editor_update_variables(self, master):
        if self.selected:
            self.length = get_entry(master, 'length', self.length)
            self.diameter = get_entry(master, 'diameter', self.diameter)
            self.mass = get_entry(master, 'mass', self.mass)
    
    def render(self, rocket, root, zoom, length_rendered, total_length, graphic_centre, normal_line_width, selected_line_width):
        if self.selected:
            line_width = selected_line_width
        else:
            line_width = normal_line_width
        
        if self.being_dragged:
            mouse_pos = pygame.mouse.get_pos()
            self.hit_box = (mouse_pos[0] - zoom*self.length/2, mouse_pos[1] - zoom*self.diameter/2, self.length*zoom, self.diameter*zoom)
            self.vertices = [(self.hit_box[0], self.hit_box[1]), (self.hit_box[0] + self.hit_box[2], self.hit_box[1]), 
                             (self.hit_box[0] + self.hit_box[2], self.hit_box[1] + self.hit_box[3]), (self.hit_box[0], self.hit_box[1] + self.hit_box[3])]

            pygame.draw.polygon(root, self.colour, self.vertices, line_width)
        else:
            start_x = graphic_centre[0] + length_rendered - total_length/2
            self.hit_box = (start_x, graphic_centre[1] - zoom*self.diameter/2, self.length*zoom, self.diameter*zoom)
            self.vertices = [(self.hit_box[0], self.hit_box[1]), (self.hit_box[0] + self.hit_box[2], self.hit_box[1]), 
                             (self.hit_box[0] + self.hit_box[2], self.hit_box[1] + self.hit_box[3]), (self.hit_box[0], self.hit_box[1] + self.hit_box[3])]

            pygame.draw.polygon(root, self.colour, self.vertices, line_width)


ROCKET_PARTS = [BodyTube, NoseCone, Engine, Fins, Decoupler]