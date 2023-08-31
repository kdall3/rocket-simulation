import pygame
import pygame_gui
import math

import geometry
import file_handler
import rocket_loader


def is_body_part(part):
    body_parts = [BodyTube, NoseCone]
    for body_part in body_parts:
        if isinstance(part, body_part):
            return True
    return False


class RocketEditor():
    def __init__(self, rocket):
        self.alive = True

        self.rocket = rocket
        self.new_part_id = 0

        self.zoom = 100
        self.auto_zoom = True
        self.zoom_multiplier = 0.95

        self.bg_colour = (36, 36, 36)
        self.part_colour = (255, 255, 255)

        self.line_width = 2
        self.selected_line_width = 5

        self.create_window()
    
    def create_window(self):
        pygame.init()

        self.window_dimensions = (1500, 700)
        self.root = pygame.display.set_mode(self.window_dimensions)
        pygame.display.set_caption('Rocket Editor')

        self.graphic_container = (300, 0, 900, 700)
        self.graphic_centre = geometry.get_box_centre(self.graphic_container)

        self.add_part_ui_container = (1200, 0, 300, 700)
        self.edit_part_ui_container = (0, 0, 300, 700)

        self.ui_manager = pygame_gui.UIManager(self.window_dimensions, 'data/themes/editor_theme.json')

        label_object_id = pygame_gui.core.ObjectID(class_id='@text_entry_labels')

        self.add_part_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(1250, 10, 200, 50), text='Add New Component', manager=self.ui_manager)
        self.add_body_tube_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(1210, 60, 280, 70), text='Body Tube', manager=self.ui_manager)
        self.add_nose_cone_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(1210, 140, 280, 70), text='Nose Cone', manager=self.ui_manager)
        self.add_engine_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(1210, 220, 280, 70), text='Engine', manager=self.ui_manager)
        self.add_fins_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(1210, 300, 280, 70), text='Fins', manager=self.ui_manager)

        self.rocket_name_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(1215, 560, 50, 50), text='Name:', object_id=label_object_id, manager=self.ui_manager)
        self.rocket_name_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(1270, 560, 220, 50), manager=self.ui_manager, initial_text=self.rocket.name)

        self.save_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(1210, 620, 135, 70), text='Save', manager=self.ui_manager)
        self.load_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(1355, 620, 135, 70), text='Load', manager=self.ui_manager)

        self.clock = pygame.time.Clock()
        
        while self.alive:
            self.time_delta = self.clock.tick(60)/1000

            self.handle_events()

            self.render()
        
        pygame.quit()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.alive = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    if geometry.check_point_in_box(mouse_pos, self.graphic_container):
                        self.deselect_all_parts()

                    # Prioritize clicks on engine
                    dragging = False
                    for part in self.rocket.parts:
                        if geometry.check_point_in_box(mouse_pos, part.shape) and isinstance(part, Engine):
                            dragging = True
                            part.being_dragged = True
                            break
                    
                    if dragging == False:
                        for part in self.rocket.parts:
                            if geometry.check_point_in_box(mouse_pos, part.shape):
                                part.being_dragged = True
                                break
                
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: # Left click released
                    mouse_pos = pygame.mouse.get_pos()

                    released_position = None
                    released_part = None

                    for position, part in enumerate(self.rocket.parts):
                        if part.being_dragged:
                            released_part = part
                            original_position = position
                        
                    if isinstance(released_part, Engine):
                        for position, part in enumerate(self.rocket.parts):
                            if geometry.check_point_in_box(mouse_pos, part.shape) and is_body_part(part):
                                released_part.parent = part
                        released_part.being_dragged = False

                    elif isinstance(released_part, Fins):
                        for position, part in enumerate(self.rocket.parts):
                            if geometry.check_point_in_box(mouse_pos, part.shape) and is_body_part(part):
                                released_part.parent = part
                            released_part.being_dragged = False

                    else:
                        for position, part in enumerate(self.rocket.parts):
                            if is_body_part(part):
                                centre = geometry.get_box_centre(part.shape)

                                if mouse_pos[0] < centre[0] and released_position == None:
                                    released_position = position

                        if released_position == None:
                            released_position = len(self.rocket.parts)

                        if released_part != None:
                            released_part.being_dragged = False
                            self.rocket.parts.insert(released_position, released_part)

                            if released_position > original_position:
                                del self.rocket.parts[original_position]
                            else:
                                del self.rocket.parts[original_position +1]

                if event.button == 3: # Right click released
                    mouse_pos = pygame.mouse.get_pos()

                    if geometry.check_point_in_box(mouse_pos, self.graphic_container):
                        self.deselect_all_parts()

                    # Prioritize clicks on engine
                    selected = False
                    for part in self.rocket.parts:
                        bounding_box = part.shape
                        if geometry.check_point_in_box(mouse_pos, bounding_box) and isinstance(part, Engine):
                            selected = True
                            self.select_part(part)
                            break
                        
                    if selected == False:
                        for part in self.rocket.parts:
                            bounding_box = part.shape
                            if geometry.check_point_in_box(mouse_pos, bounding_box):
                                self.select_part(part)
                                break

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.add_body_tube_button:
                    self.add_body_tube()
                elif event.ui_element == self.add_nose_cone_button:
                    self.add_nose_cone()
                elif event.ui_element == self.add_engine_button:
                    self.add_engine()
                elif event.ui_element == self.add_fins_button:
                    self.add_fins()
                elif event.ui_element == self.save_button:
                    self.save_design()
                elif event.ui_element == self.load_button:
                    self.load_design()
                else:
                    try:
                        if event.ui_element == self.delete_part_button:
                            self.delete_selected_part()
                    except AttributeError:
                        pass
                
            if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                if event.ui_element == self.rocket_name_entry:
                    self.rocket.name = self.rocket_name_entry.get_text()

                try:
                    if event.ui_element == self.mass_entry:
                        self.get_selected_part().mass_override = True
                except AttributeError:
                    pass
                    
                try:
                    if event.ui_element == self.density_entry:
                        self.get_selected_part().mass_override = False
                        self.mass_entry.set_text(str(round(self.get_selected_part().mass, 3)))
                except AttributeError:
                    pass

            self.ui_manager.process_events(event)
        
        self.ui_manager.update(self.time_delta)

    def render(self):
        self.root.fill(self.bg_colour)

        self.total_length = 0
        self.max_diameter = 0

        for part in self.rocket.parts:
            if is_body_part(part):
                self.total_length += part.length
            if isinstance(part, Fins):
                if part.parent.diameter + 2 * part.width > self.max_diameter:
                    self.max_diameter = part.parent.diameter + 2 * part.width
            else:
                if part.diameter > self.max_diameter:
                    self.max_diameter = part.diameter

        if self.auto_zoom:
            try:
                if self.total_length / self.graphic_container[2] > self.max_diameter / self.graphic_container[3]:
                    self.zoom = self.zoom_multiplier * self.graphic_container[2] / self.total_length
                else:
                    self.zoom = self.zoom_multiplier * self.graphic_container[3] / self.max_diameter
            except ZeroDivisionError:
                self.zoom = 1

        self.length_rendered = 0
        self.total_length = self.total_length * self.zoom

        for part in self.rocket.parts:
            if hasattr(part, 'render'):
                part.render(self)
                if isinstance(part, BodyTube) or isinstance(part, NoseCone):
                    self.length_rendered += part.length * self.zoom
        
        pygame.draw.rect(self.root, (50, 50, 50), self.add_part_ui_container)
        pygame.draw.rect(self.root, (50, 50, 50), self.edit_part_ui_container)

        self.ui_manager.draw_ui(self.root)

        pygame.display.update()

    def select_part(self, selected_part):
        for part in self.rocket.parts:
            if part.part_id == selected_part.part_id and not part.selected:
                part.selected = True
                self.open_part_editor(selected_part)
            elif part.part_id != selected_part.part_id and part.selected:
                self.deselect_part(part)

    def deselect_part(self, deselected_part):
        for part in self.rocket.parts:
            if part.part_id == deselected_part.part_id and part.selected:
                part.selected = False
                self.close_part_editor(deselected_part)
    
    def get_selected_part(self):
        for part in self.rocket.parts:
            if part.selected:
                return part
    
    def deselect_all_parts(self):
        for part in self.rocket.parts:
            self.deselect_part(part)
    
    def delete_selected_part(self):
        for position, part in enumerate(self.rocket.parts):
            if part.selected:
                self.deselect_part(part)
                del self.rocket.parts[position]
    
    def get_last_body_part_index(self):
        index = -1
        while True:
            if is_body_part(self.rocket.parts[index]):
                return len(self.rocket.parts) + index
            if abs(index) > len(self.rocket.parts):
                return 0
            index -= 1

    def save_design(self):
        self.deselect_all_parts()
        file_handler.save_rocket(self.rocket, self.rocket.name)
    
    def load_design(self):
        self.alive = False

        rocket_loader.run('editor', 'editor')

    def add_body_tube(self):
        self.rocket.parts.append(BodyTube(colour=self.part_colour, part_id=self.new_part_id))
        self.new_part_id += 1
    
    def add_nose_cone(self):
        self.rocket.parts.insert(0, NoseCone(colour=self.part_colour, part_id=self.new_part_id))
        self.new_part_id += 1
    
    def add_engine(self):
        self.rocket.parts.append(Engine(self.rocket.parts[self.get_last_body_part_index()], part_id=self.new_part_id))
        self.new_part_id += 1
    
    def add_fins(self):
        self.rocket.parts.append(Fins(self.rocket.parts[self.get_last_body_part_index()], part_id=self.new_part_id))
        self.new_part_id += 1

    def open_part_editor(self, part):
        allowed_digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']

        label_object_id = pygame_gui.core.ObjectID(class_id='@text_entry_labels')

        label_start_x = 20
        label_width = 132
        label_height = 50

        entry_start_x = 150
        entry_width = 140
        entry_height = 50

        length_limit = 10

        self.delete_part_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(150, 640, 140, 50), text='Delete', manager=self.ui_manager)

        if isinstance(part, BodyTube):
            self.body_tube_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, 10, 300, 50), text=f'Edit Body Tube', manager=self.ui_manager)

            self.length_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(label_start_x, 60, label_width, label_height), manager=self.ui_manager, text='Length:', object_id=label_object_id)
            self.length_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(entry_start_x, 60, entry_width, entry_height), manager=self.ui_manager, initial_text=str(float(part.length)))
            self.length_entry.allowed_characters = allowed_digits

            self.diameter_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(label_start_x, 120, label_width, label_height), manager=self.ui_manager, text='Diameter:', object_id=label_object_id)
            self.diameter_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(entry_start_x, 120, entry_width, entry_height), manager=self.ui_manager, initial_text=str(float(part.diameter)))
            self.diameter_entry.allowed_characters = allowed_digits

            self.wall_thickness_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(label_start_x, 180, label_width, label_height), manager=self.ui_manager, text='Wall Thickness:', object_id=label_object_id)
            self.wall_thickness_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(entry_start_x, 180, entry_width, entry_height), manager=self.ui_manager, initial_text=str(float(part.wall_thickness)))
            self.wall_thickness_entry.allowed_characters = allowed_digits

            self.density_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(label_start_x, 520, label_width, label_height), manager=self.ui_manager, text='Density:', object_id=label_object_id)
            self.density_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(entry_start_x, 520, entry_width, entry_height), manager=self.ui_manager, initial_text=str(float(part.density)))
            self.density_entry.allowed_characters = allowed_digits

            self.mass_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(label_start_x, 580, label_width, label_height), manager=self.ui_manager, text='Mass:', object_id=label_object_id)
            self.mass_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(entry_start_x, 580, entry_width, entry_height), manager=self.ui_manager, initial_text=str(round(float(part.mass), length_limit)))
            self.mass_entry.allowed_characters = allowed_digits
            self.mass_entry.length_limit = length_limit

        elif isinstance(part, NoseCone):
            self.nose_cone_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, 10, 300, 50), text=f'Edit Nose Cone', manager=self.ui_manager)

            self.length_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(label_start_x, 60, label_width, label_height), manager=self.ui_manager, text='Length:', object_id=label_object_id)
            self.length_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(entry_start_x, 60, entry_width, entry_height), manager=self.ui_manager, initial_text=str(float(part.length)))
            self.length_entry.allowed_characters = allowed_digits

            self.diameter_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(label_start_x, 120, label_width, label_height), manager=self.ui_manager, text='Diameter:', object_id=label_object_id)
            self.diameter_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(entry_start_x, 120, entry_width, entry_height), manager=self.ui_manager, initial_text=str(float(part.diameter)))
            self.diameter_entry.allowed_characters = allowed_digits

            self.mass_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(label_start_x, 580, label_width, label_height), manager=self.ui_manager, text='Mass:', object_id=label_object_id)
            self.mass_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(entry_start_x, 580, entry_width, entry_height), manager=self.ui_manager, initial_text=str(round(float(part.mass), length_limit)))
            self.mass_entry.allowed_characters = allowed_digits
        
        elif isinstance(part, Engine):
            self.engine_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, 10, 300, 50), text=f'Edit Engine', manager=self.ui_manager)

            self.length_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(label_start_x, 60, label_width, label_height), manager=self.ui_manager, text='Length:', object_id=label_object_id)
            self.length_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(entry_start_x, 60, entry_width, 50), manager=self.ui_manager, initial_text=str(float(part.length)))
            self.length_entry.allowed_characters = allowed_digits

            self.diameter_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(label_start_x, 120, label_width, label_height), manager=self.ui_manager, text='Diameter:', object_id=label_object_id)
            self.diameter_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(entry_start_x, 120, entry_width, entry_height), manager=self.ui_manager, initial_text=str(float(part.diameter)))
            self.diameter_entry.allowed_characters = allowed_digits

            self.mass_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(label_start_x, 580, label_width, label_height), manager=self.ui_manager, text='Mass:', object_id=label_object_id)
            self.mass_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(entry_start_x, 580, entry_width, entry_height), manager=self.ui_manager, initial_text=str(round(float(part.mass), length_limit)))
            self.mass_entry.allowed_characters = allowed_digits
        
        elif isinstance(part, Fins):
            self.fins_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, 10, 300, 50), text=f'Edit Fins', manager=self.ui_manager)

            self.length_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(label_start_x, 60, label_width, label_height), manager=self.ui_manager, text='Length:', object_id=label_object_id)
            self.length_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(entry_start_x, 60, entry_width, entry_height), manager=self.ui_manager, initial_text=str(float(part.length)))
            self.length_entry.allowed_characters = allowed_digits

            self.width_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(label_start_x, 120, label_width, label_height), manager=self.ui_manager, text='Width:', object_id=label_object_id)
            self.width_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(entry_start_x, 120, entry_width, entry_height), manager=self.ui_manager, initial_text=str(float(part.width)))
            self.width_entry.allowed_characters = allowed_digits

            self.offset_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(label_start_x, 180, label_width, label_height), manager=self.ui_manager, text='Offset:', object_id=label_object_id)
            self.offset_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(entry_start_x, 180, entry_width, entry_height), manager=self.ui_manager, initial_text=str(float(part.offset)))
            self.offset_entry.allowed_characters = allowed_digits + ['-']

            self.mass_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(label_start_x, 580, label_width, label_height), manager=self.ui_manager, text='Mass:', object_id=label_object_id)
            self.mass_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(entry_start_x, 580, entry_width, entry_height), manager=self.ui_manager, initial_text=str(round(float(part.mass), length_limit)))
            self.mass_entry.allowed_characters = allowed_digits
            self.mass_entry.length_limit = length_limit

    def close_part_editor(self, part):
        self.delete_part_button.kill()

        if isinstance(part, BodyTube):
            self.body_tube_label.kill()
            self.length_label.kill()
            self.length_entry.kill()
            self.diameter_label.kill()
            self.diameter_entry.kill()
            self.wall_thickness_label.kill()
            self.wall_thickness_entry.kill()
            self.density_label.kill()
            self.density_entry.kill()
            self.mass_label.kill()
            self.mass_entry.kill()

        elif isinstance(part, NoseCone):
            self.nose_cone_label.kill()
            self.length_label.kill()
            self.length_entry.kill()
            self.diameter_label.kill()
            self.diameter_entry.kill()
            self.mass_label.kill()
            self.mass_entry.kill()

        elif isinstance(part, Engine):
            self.engine_label.kill()
            self.length_label.kill()
            self.length_entry.kill()
            self.diameter_label.kill()
            self.diameter_entry.kill()
            self.mass_label.kill()
            self.mass_entry.kill()

        elif isinstance(part, Fins):
            self.fins_label.kill()
            self.length_label.kill()
            self.length_entry.kill()
            self.width_label.kill()
            self.width_entry.kill()
            self.offset_label.kill()
            self.offset_entry.kill()
            self.mass_label.kill()
            self.mass_entry.kill()


class Rocket():
    def __init__(self, name='New Rocket', parts=[]):
        self.name = name
        self.parts = parts


class BodyTube():
    def __init__(self, length=1, diameter=0.3, wall_thickness=0.01, density=1330, colour=(255, 255, 255), part_id=None):
        self.length = length
        self.diameter = diameter
        self.wall_thickness = wall_thickness
        self.density = density
        self.mass = self.get_mass()

        self.part_id = part_id

        self.colour = colour

        self.being_dragged = False
        self.selected = False
        self.mass_override = False

        self.shape = (0, 0, 0, 0)
        
    def update_variables(self, master):
        if self.selected:
            try:
                if float(master.length_entry.get_text()) != 0:
                    self.length = float(master.length_entry.get_text())
                if float(master.diameter_entry.get_text()) != 0:
                    self.diameter = float(master.diameter_entry.get_text())
                if float(master.wall_thickness_entry.get_text()) != 0:
                    self.wall_thickness = float(master.wall_thickness_entry.get_text())
                if float(master.density_entry.get_text()) != 0 and not self.mass_override:
                    self.density = float(master.density_entry.get_text())
                if not self.mass_override:
                    self.mass = self.get_mass()
                elif float(master.mass_entry.get_text()) != 0 and self.mass_override:
                    self.mass = float(master.mass_entry.get_text())
            except AttributeError:
                pass
            except ValueError:
                pass
    
    def get_mass(self):
        return self.density * math.pi * self.length * (self.diameter**2 - (self.diameter - self.wall_thickness)**2) / 4
    
    def render(self, master):
        self.update_variables(master)

        if self.selected:
            line_width = master.selected_line_width
        else:
            line_width = master.line_width
        
        if self.being_dragged:
            mouse_pos = pygame.mouse.get_pos()
            self.shape = (mouse_pos[0] - master.zoom*self.length/2, mouse_pos[1] - master.zoom*self.diameter/2, self.length*master.zoom, self.diameter*master.zoom)
            pygame.draw.rect(master.root, self.colour, self.shape, line_width)
        else:
            start_x = master.graphic_centre[0] + master.length_rendered - master.total_length/2
            self.shape = (start_x, master.graphic_centre[1] - master.zoom*self.diameter/2, self.length*master.zoom, self.diameter*master.zoom)
            pygame.draw.rect(master.root, self.colour, self.shape, line_width)


class NoseCone():
    def __init__(self, cone_shape='conic', length=0.3, diameter=0.3, density=1330, colour=(255, 255, 255), part_id=None):
        self.cone_shape = cone_shape

        self.length = length
        self.diameter = diameter
        self.density = density
        self.mass = self.get_mass()

        self.part_id = part_id

        self.colour = colour

        self.being_dragged = False
        self.selected = False
        self.mass_override = False

        self.shape = (0, 0, 0, 0)
    
    def update_variables(self, master):
        if self.selected:
            try:
                if float(master.length_entry.get_text()) != 0:
                    self.length = float(master.length_entry.get_text())
                if float(master.diameter_entry.get_text()) != 0:
                    self.diameter = float(master.diameter_entry.get_text())
            except AttributeError:
                pass
            except ValueError:
                pass
    
    def get_mass(self):
        if self.cone_shape == 'conic':
            return math.pi * (self.diameter/2)**2 * self.length/3
        else:
            raise Exception('Invalid cone shape')

    def render(self, master):
        self.update_variables(master)

        if self.selected:
            line_width = master.selected_line_width
        else:
            line_width = master.line_width

        if self.being_dragged:
            mouse_pos = pygame.mouse.get_pos()

            if self.cone_shape == 'conic':
                self.shape = (mouse_pos[0] - master.zoom*self.length/2, mouse_pos[1] - master.zoom*self.diameter/2, self.length*master.zoom, self.diameter*master.zoom)
                pygame.draw.polygon(master.root, self.colour, [(self.shape[0], mouse_pos[1]), (self.shape[0] + self.shape[2], self.shape[1]), 
                                                            (self.shape[0] + self.shape[2], self.shape[1] + self.shape[3])], line_width)
        else:
            if self.cone_shape == 'conic':
                start_x = master.graphic_centre[0] + master.length_rendered - master.total_length/2
                self.shape = (start_x, master.graphic_centre[1] - master.zoom*self.diameter/2, self.length*master.zoom, self.diameter*master.zoom)
                pygame.draw.polygon(master.root, self.colour, [(self.shape[0], master.graphic_centre[1]), (self.shape[0] + self.shape[2], self.shape[1]), 
                                                            (self.shape[0] + self.shape[2], self.shape[1] + self.shape[3])], line_width)


class Engine():
    def __init__(self, parent, length=0.5, diameter=0.1, mass=1, offset=0, colour=(255, 255, 255), part_id=None):
        self.length = length
        self.diameter = diameter
        self.mass = mass
        self.offset = offset

        self.colour = colour

        self.part_id = part_id

        self.parent = parent

        self.being_dragged = False
        self.selected = False
        self.mass_override = True

        self.shape = (0, 0, 0, 0)
    
    def update_variables(self, master):
        for part in master.rocket.parts:
            if part.part_id == self.parent.part_id:
                self.parent = part

        if self.selected:
            try:
                if float(master.length_entry.get_text()) != 0:
                    self.length = float(master.length_entry.get_text())
                if float(master.diameter_entry.get_text()) != 0:
                    self.diameter = float(master.diameter_entry.get_text())
                if float(master.mass_entry.get_text()) != 0:
                    self.mass = float(master.mass_entry.get_text())
            except AttributeError:
                pass
            except ValueError:
                pass
    
    def render(self, master):
        self.update_variables(master)

        if self.selected:
            line_width = master.selected_line_width
        else:
            line_width = master.line_width

        if self.being_dragged:
            mouse_pos = pygame.mouse.get_pos()
            self.shape = (mouse_pos[0] - master.zoom*self.length/2, mouse_pos[1] - master.zoom*self.diameter/2, self.length*master.zoom, self.diameter*master.zoom)
            pygame.draw.rect(master.root, self.colour, self.shape, line_width)
        else:
            parent_centre = geometry.get_box_centre(self.parent.shape)
            start_x = self.parent.shape[0] + self.parent.shape[2] + self.offset - self.length*master.zoom 
            start_y = parent_centre[1] - (self.diameter/2)*master.zoom
            self.shape = (start_x, start_y, self.length*master.zoom, self.diameter*master.zoom)
            pygame.draw.rect(master.root, self.colour, self.shape, line_width)


class Fins():
    def __init__(self, parent, fin_shape='triangle', fin_count=4, length=0.2, thickness=0.05, width=0.1, offset=0, mass=1, colour=(255, 255, 255), part_id=None):
        self.fin_shape = fin_shape
        self.fin_count = fin_count

        self.width = width

        self.length = length
        self.thickness = thickness
        self.offset = offset
        self.mass = mass

        self.colour = colour

        self.part_id = part_id

        self.parent = parent

        self.being_dragged = False
        self.selected = False
        self.mass_override = False

        self.shape = (0, 0, 0, 0)
    
    def update_variables(self, master):
        for part in master.rocket.parts:
            if part.part_id == self.parent.part_id:
                self.parent = part

        if self.selected:
            try:
                if float(master.length_entry.get_text()) != 0:
                    self.length = float(master.length_entry.get_text())
                if float(master.width_entry.get_text()) != 0:
                    self.width = float(master.width_entry.get_text())

                self.offset = float(master.offset_entry.get_text())
            except AttributeError:
                pass
            except ValueError:
                pass
    
    def render(self, master):
        self.update_variables(master)

        if self.selected:
            line_width = master.selected_line_width
        else:
            line_width = master.line_width
        
        if self.being_dragged:
            mouse_pos = pygame.mouse.get_pos()
            if self.fin_shape == 'triangle':
                start_x = mouse_pos[0] - (self.length/2)*master.zoom
                self.shape = [(start_x, mouse_pos[1] - self.parent.shape[3]/2 - self.width*master.zoom, self.length*master.zoom, self.width*master.zoom),
                              (start_x, mouse_pos[1] + self.parent.shape[3]/2, self.length*master.zoom, self.width*master.zoom)]
                pygame.draw.polygon(master.root, self.colour, [(self.shape[0][0], self.shape[0][1] + self.shape[0][3]), (self.shape[0][0] + self.shape[0][2], self.shape[0][1] + self.shape[0][3]),
                                                               (self.shape[0][0] + self.shape[0][2], self.shape[0][1])], line_width)
                pygame.draw.polygon(master.root, self.colour, [(self.shape[1][0], self.shape[1][1]), (self.shape[1][0] + self.shape[1][2], self.shape[1][1]),
                                                               (self.shape[1][0] + self.shape[1][2], self.shape[1][1] + self.shape[1][3])], line_width)
        else:
            if self.fin_shape == 'triangle':
                start_x = self.parent.shape[0] + self.parent.shape[2] + self.offset*master.zoom - self.length*master.zoom 
                self.shape = [(start_x, self.parent.shape[1]-self.width*master.zoom, self.length*master.zoom, self.width*master.zoom), 
                              (start_x, self.parent.shape[1]+self.parent.shape[3], self.length*master.zoom, self.width*master.zoom)]
                pygame.draw.polygon(master.root, self.colour, [(self.shape[0][0], self.parent.shape[1]), (self.shape[0][0] + self.shape[0][2], self.parent.shape[1]),
                                                               (self.shape[0][0] + self.shape[0][2], self.shape[0][1])], line_width)
                pygame.draw.polygon(master.root, self.colour, [(self.shape[1][0], self.shape[1][1]), (self.shape[1][0] + self.shape[1][2], self.shape[1][1]),
                                                               (self.shape[1][0] + self.shape[1][2], self.shape[1][1] + self.shape[1][3])], line_width)


def run(rocket=Rocket()):
    RocketEditor(rocket)
