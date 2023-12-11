import pygame
import pygame_gui
import matplotlib.pyplot as plt
import math

import os

import geometry
import db_controller
import rocket_renderer
import rocket_simulator
from rocket_parts import *

class MainMenu():
    def __init__(self):
        self.alive = True

        self.bg_colour = (36, 36, 36)

        self.create_window()
    
    def create_window(self):
        self.window_dimensions = (700, 700)
        self.monitor_dimensions = (1920, 1080)
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % ((self.monitor_dimensions[0]-self.window_dimensions[0])/2,(self.monitor_dimensions[1]-self.window_dimensions[1])/2)

        pygame.init()

        self.root = pygame.display.set_mode(self.window_dimensions)
        pygame.display.set_caption('Rocket Simulation')

        self.ui_manager = pygame_gui.UIManager(self.window_dimensions, 'data/themes/menu_theme.json')

        title_object_id = pygame_gui.core.ObjectID(class_id='@title_labels')

        title_width = 400

        button_width = 400
        button_height = 100

        self.title_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(self.window_dimensions[0]/2-title_width/2, 55, title_width, 100), text='Rocket Simulation', object_id=title_object_id, manager=self.ui_manager)

        self.create_rocket_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(self.window_dimensions[0]/2-button_width/2, 200, button_width, button_height), text='Create New Rocket', manager=self.ui_manager)
        self.edit_rocket_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(self.window_dimensions[0]/2-button_width/2, 320, button_width, button_height), text='Edit Saved Rocket', manager=self.ui_manager)
        self.create_simulation_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(self.window_dimensions[0]/2-button_width/2, 440, button_width, button_height), text='Create New Simulation', manager=self.ui_manager)

        self.clock = pygame.time.Clock()

        while self.alive:
            self.time_delta = self.clock.tick(60)/1000

            self.handle_events()

            self.render()
        
        pygame.quit()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
            
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.create_rocket_button:
                    self.create_rocket()
                elif event.ui_element == self.edit_rocket_button:
                    self.edit_rocket()
                elif event.ui_element == self.create_simulation_button:
                    self.create_simulation()
                elif event.ui_element == self.edit_simulation_button:
                    self.edit_simulation()
        
            self.ui_manager.process_events(event)
        
        self.ui_manager.update(self.time_delta)
    
    def render(self):
        self.root.fill(self.bg_colour)

        self.ui_manager.draw_ui(self.root)

        pygame.display.update()
    
    def close(self):
        self.alive = False
        pygame.quit()

    def create_rocket(self):
        self.close()

        Editor()

    def edit_rocket(self):
        self.close()

        RocketLoader('main menu', 'editor')
    
    def create_simulation(self):
        self.close()

        RocketLoader('main menu', 'simulator')

    def view_simulation(self):
        pass


class RocketLoader():
    def __init__(self, last_window, target_window):
        self.last_window = last_window
        self.target_window = target_window

        self.alive = True

        self.bg_colour = (36, 36, 36)

        self.rockets = db_controller.get_all_saved_rockets()

        self.create_window()
    
    def create_window(self):
        pygame.init()

        self.font = pygame.font.Font('data/fonts/Rubik-Regular.ttf', 20)

        self.window_dimensions = (700, 700)
        self.root = pygame.display.set_mode(self.window_dimensions)
        pygame.display.set_caption('Rocket Simulation')

        self.rocket_list_container = (50, 100, 600, 500)

        self.listing_separation = 10
        self.listing_height = 90
        self.listing_difference = self.listing_height + self.listing_separation

        self.scroll_position = 0
        self.scroll_increment = 10

        title_width = 300
        title_object_id = pygame_gui.core.ObjectID(class_id='@title_labels')

        self.rect_list = []

        self.selected_index = None

        self.ui_manager = pygame_gui.UIManager(self.window_dimensions, 'data/themes/rocket_loader_theme.json')

        self.title_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(self.window_dimensions[0]/2-title_width/2, 10, title_width, 80), text='Load Rocket:', object_id=title_object_id, manager=self.ui_manager)

        self.load_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(50, (self.rocket_list_container[1] + self.rocket_list_container[3] + self.window_dimensions[1])/2-37.5, 200, 75), text='Load', manager=self.ui_manager)
        self.delete_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(450, (self.rocket_list_container[1] + self.rocket_list_container[3] + self.window_dimensions[1])/2-37.5, 200, 75), text='Delete', manager=self.ui_manager)
        self.load_button.disable()
        self.delete_button.disable()

        self.clock = pygame.time.Clock()
        
        while self.alive:
            self.time_delta = self.clock.tick(60)/1000

            self.handle_events()

            self.render()
        
        pygame.quit()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.back_to_last_window()

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.load_button:
                    self.load_selected_rocket()
                elif event.ui_element == self.delete_button:
                    self.delete_selected_rocket()

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 or event.button == 3:
                    listing_clicked = False
                    mouse_pos = pygame.mouse.get_pos()
                    for i, rect in enumerate(self.rect_list):
                        if rect != None:
                            if geometry.check_point_in_box(mouse_pos, rect):
                                self.selected_index = i
                                self.load_button.enable()
                                self.delete_button.enable()
                                listing_clicked = True
                    if listing_clicked == False and geometry.check_point_in_box(mouse_pos, self.rocket_list_container):
                        self.selected_index = None
                        self.load_button.disable()
                        self.delete_button.disable()

            if event.type == pygame.MOUSEWHEEL:
                self.scroll_position += self.scroll_increment*event.y*-1
                if self.scroll_position < 0:
                    self.scroll_position = 0
                elif len(self.rockets)*self.listing_difference < self.rocket_list_container[3]:
                    self.scroll_position = 0
                elif self.scroll_position > len(self.rockets)*self.listing_difference - self.rocket_list_container[3]:
                    self.scroll_position = len(self.rockets)*self.listing_difference - self.rocket_list_container[3]
            
            self.ui_manager.process_events(event)
        
        self.ui_manager.update(self.time_delta)

    def render(self):
        self.root.fill(self.bg_colour)

        self.rect_list = []

        for i, rocket in enumerate(self.rockets):
            start_y = (i+1)*self.listing_difference - self.scroll_position

            if start_y > self.rocket_list_container[1] - self.listing_height and start_y < self.rocket_list_container[1] + self.rocket_list_container[3]:
                rect = (self.rocket_list_container[0], start_y, self.rocket_list_container[2], self.listing_height)

                pygame.draw.rect(self.root, (69, 73, 78), rect, border_radius=3)
                if i == self.selected_index and rect[3] >= 10: # Have to check if the height is greater than 10 because otherwise the border radius will be too big
                    pygame.draw.rect(self.root, (255, 255, 255), rect, border_radius=3, width=3)

                rocket_visual_container = (rect[0]+rect[2]-200, rect[1]+10, 180, rect[3]-20)

                rocket_renderer.render_rocket_editor(rocket, self.root, rocket_visual_container, self.font, normal_line_width=1, selected_line_width=1)

                name_surface = self.font.render(rocket.name, True, (255, 255, 255))
                self.root.blit(name_surface, (rect[0]+10, rect[1]+10))

                self.rect_list.append(rect)
            else:
                self.rect_list.append(None)

        pygame.draw.rect(self.root, self.bg_colour, (0, 0, self.window_dimensions[0], self.rocket_list_container[1]))
        pygame.draw.rect(self.root, self.bg_colour, (0, self.rocket_list_container[1]+self.rocket_list_container[3], self.window_dimensions[0], self.window_dimensions[1] - (self.rocket_list_container[1]+self.rocket_list_container[3])))

        self.ui_manager.draw_ui(self.root)

        pygame.display.update()
    
    def close(self):
        self.alive = False
        pygame.quit()
    
    def back_to_last_window(self):
        self.close()

        if self.last_window == 'main menu':
            MainMenu()
        elif self.last_window == 'editor':
            Editor()
        else:
            raise Exception('Invalid last window')
    
    def delete_selected_rocket(self):
        if self.selected_index != None:
            db_controller.delete_rocket(self.rockets[self.selected_index])
            self.rockets = db_controller.get_all_saved_rockets()
            self.selected_index = None
    
    def load_selected_rocket(self):
        if self.selected_index != None:
            self.close()
            if self.target_window == 'editor':
                Editor(self.rockets[self.selected_index])
            elif self.target_window == 'simulator':
                SimulationPlayer(self.rockets[self.selected_index])
            else:
                raise Exception('Invalid target window')


class Editor():
    def __init__(self, rocket=Rocket()):
        self.alive = True

        self.rocket = rocket

        self.zoom = 100
        self.auto_zoom = True
        self.zoom_multiplier = 0.95

        self.bg_colour = (36, 36, 36)
        self.part_colour = (255, 255, 255)

        self.normal_line_width = 2
        self.selected_line_width = 5

        self.length_unit = 'm'
        self.mass_unit = 'kg'
        self.force_unit = 'N'
        self.time_unit = 's'

        self.create_window()

    def create_window(self):
        self.window_dimensions = (1500, 700)
        self.monitor_dimensions = (1920, 1080)
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % ((self.monitor_dimensions[0]-self.window_dimensions[0])/2,(self.monitor_dimensions[1]-self.window_dimensions[1])/2)

        pygame.init()

        self.font = pygame.font.Font('data/fonts/Rubik-Regular.ttf', 20)

        self.root = pygame.display.set_mode(self.window_dimensions)
        pygame.display.set_caption('Rocket Editor')

        self.graphic_container = (300, 0, 900, 700)
        self.graphic_centre = geometry.get_box_centre(self.graphic_container)

        self.right_panel_ui_container = (1200, 0, 300, 700)
        self.left_panel_ui_container = (0, 0, 300, 700)

        self.ui_manager = pygame_gui.UIManager(self.window_dimensions, 'data/themes/editor_theme.json')

        label_object_id = pygame_gui.core.ObjectID(class_id='@text_entry_labels')

        self.add_part_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(1250, 10, 200, 50), text='Add New Component', manager=self.ui_manager)
        self.add_body_tube_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(1210, 60, 280, 70), text='Body Tube', manager=self.ui_manager)
        self.add_nose_cone_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(1210, 140, 280, 70), text='Nose Cone', manager=self.ui_manager)
        self.add_decoupler_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(1210, 220, 280, 70), text='Decoupler', manager=self.ui_manager)
        self.add_engine_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(1210, 300, 280, 70), text='Engine', manager=self.ui_manager)
        self.add_fins_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(1210, 380, 280, 70), text='Fins', manager=self.ui_manager)

        self.rocket_name_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(1215, 560, 50, 50), text='Name:', object_id=label_object_id, manager=self.ui_manager)
        self.rocket_name_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(1270, 560, 220, 50), manager=self.ui_manager, initial_text=self.rocket.name)
        self.rocket_name_entry.set_text_length_limit(26)

        self.save_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(1210, 620, 135, 70), text='Save', manager=self.ui_manager)
        self.load_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(1355, 620, 135, 70), text='Load', manager=self.ui_manager)

        self.open_info_panel()

        self.clock = pygame.time.Clock()
        
        while self.alive:
            self.time_delta = self.clock.tick(60)/1000

            self.handle_events()

            self.render()
        
        pygame.quit()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                return None
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    if geometry.check_point_in_box(mouse_pos, self.graphic_container):
                        self.deselect_all_parts()

                    # Prioritize clicks on engine
                    dragging = False
                    for part in self.rocket.parts:
                        if part.check_point_in_hit_box(mouse_pos) and isinstance(part, Engine):
                            dragging = True
                            part.being_dragged = True
                            break
                    
                    if dragging == False:
                        for part in self.rocket.parts:
                            if part.check_point_in_hit_box(mouse_pos):
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
                            if part.check_point_in_hit_box(mouse_pos) and check_part_type(part, [BodyTube, NoseCone, Decoupler]):
                                released_part.parent_id = part.local_part_id
                        released_part.being_dragged = False

                    elif isinstance(released_part, Fins):
                        for position, part in enumerate(self.rocket.parts):
                            if part.check_point_in_hit_box(mouse_pos) and check_part_type(part, [BodyTube, NoseCone, Decoupler]):
                                released_part.parent_id = part.local_part_id
                            released_part.being_dragged = False

                    else:
                        for position, part in enumerate(self.rocket.parts):
                            if check_part_type(part, [BodyTube, NoseCone, Decoupler]):
                                centre = geometry.get_centroid_poly(part.hit_box)

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

                elif event.button == 3: # Right click released
                    mouse_pos = pygame.mouse.get_pos()

                    if geometry.check_point_in_box(mouse_pos, self.graphic_container):
                        self.deselect_all_parts()

                    # Prioritize clicks on engine
                    selected = False
                    for part in self.rocket.parts:
                        if part.check_point_in_hit_box(mouse_pos) and isinstance(part, Engine):
                            selected = True
                            self.select_part(part)
                            break
                        
                    if selected == False:
                        for part in self.rocket.parts:
                            if part.check_point_in_hit_box(mouse_pos):
                                self.select_part(part)
                                break

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.add_body_tube_button:
                    self.add_body_tube()
                elif event.ui_element == self.add_nose_cone_button:
                    self.add_nose_cone()
                elif event.ui_element == self.add_decoupler_button:
                    self.add_decoupler()
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
                        if event.ui_element == self.part_editor_elements['delete part button']:
                            self.delete_selected_part()
                    except AttributeError:
                        pass

                    try:
                        if event.ui_element == self.info_panel_elements['simulate button']:
                            self.close()
                            SimulationPlayer(self.rocket)
                    except AttributeError:
                        pass
                
            if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                if event.ui_element == self.rocket_name_entry:
                    self.rocket.name = self.rocket_name_entry.get_text()

                try:
                    if event.ui_element == self.part_editor_elements['mass entry']:
                        self.get_selected_part().mass_override = True
                except KeyError:
                    pass
                except AttributeError:
                    pass
                    
                try:
                    if event.ui_element == self.part_editor_elements['density entry']:
                        self.get_selected_part().mass_override = False
                        self.mass_entry.set_text(str(round(self.get_selected_part().mass, 3)))
                except KeyError:
                    pass
                except AttributeError:
                    pass

                try:
                    if event.ui_element == self.part_editor_elements['stage entry']:
                        part = self.get_selected_part()
                        entered_stage = int(self.part_editor_elements['stage entry'].get_text())

                        # Add part to stages
                        if entered_stage < len(self.rocket.stages):
                            len_before_delete = len(self.rocket.stages)
                            self.delete_part_from_stages(part)
                            if len_before_delete == len(self.rocket.stages): # Check whether a stage number has been deleted
                                self.rocket.stages[entered_stage].append(part.local_part_id)
                            else:
                                self.rocket.stages[entered_stage-1].append(part.local_part_id)
                            
                        elif entered_stage >= len(self.rocket.stages):
                            self.delete_part_from_stages(part)
                            self.rocket.stages.append([part.local_part_id])
                            self.self.part_editor_elements['stage entry'].set_text(str(len(self.rocket.stages)))
                except Exception:
                    pass

            self.ui_manager.process_events(event)
        
        self.ui_manager.update(self.time_delta)

    def render(self):
        self.root.fill(self.bg_colour)

        self.update_all_parts()
        rocket_renderer.render_rocket_editor(self.rocket, self.root, self.graphic_container, self.font, show_stages=True)
        
        pygame.draw.rect(self.root, (50, 50, 50), self.right_panel_ui_container)
        pygame.draw.rect(self.root, (50, 50, 50), self.left_panel_ui_container)

        self.update_info_panel()

        self.ui_manager.draw_ui(self.root)

        pygame.display.update()
    
    def close(self):
        self.alive = False
        pygame.quit()

    def select_part(self, selected_part):
        self.deselect_all_parts()

        for part in self.rocket.parts:
            if part.local_part_id == selected_part.local_part_id and not part.selected:
                part.selected = True
                self.open_part_editor(selected_part)
                break

    def deselect_part(self, deselected_part):
        for part in self.rocket.parts:
            if part.local_part_id == deselected_part.local_part_id and part.selected:
                part.selected = False
                self.close_part_editor()
    
    def get_selected_part(self):
        for part in self.rocket.parts:
            if part.selected:
                return part
    
    def get_part_stage(self, part):
        for stage_num, stage in enumerate(self.rocket.stages):
            if part.local_part_id in stage:
                return stage_num
        return None
    
    def deselect_all_parts(self):
        for part in self.rocket.parts:
            self.deselect_part(part)
    
    def delete_selected_part(self):
        for position, part in enumerate(self.rocket.parts):
            if part.selected:
                self.deselect_part(part)
                del self.rocket.parts[position]
                self.delete_part_from_stages(part)
    
    def delete_part_from_stages(self, part):
        for stage in self.rocket.stages:
            if part.local_part_id in stage:
                stage.remove(part.local_part_id)
                if len(stage) == 0:
                    self.rocket.stages.remove(stage)
    
    def get_last_part_in_whitelist(self, part_whitelist):
        index = -1
        while True:
            if check_part_type(self.rocket.parts[index], part_whitelist):
                return len(self.rocket.parts) + index
            if abs(index) > len(self.rocket.parts):
                return 0
            index -= 1
    
    def update_all_parts(self):
        for part in self.rocket.parts:
            if hasattr(part, 'editor_update_variables'):
                part.editor_update_variables(self)

    def save_design(self):
        self.deselect_all_parts()
        db_controller.save_rocket(self.rocket)
    
    def load_design(self):
        self.close()

        RocketLoader('editor', 'editor')

    def add_body_tube(self):
        self.rocket.parts.append(BodyTube(colour=self.part_colour, local_part_id=self.rocket.new_part_id))
        self.rocket.new_part_id += 1
    
    def add_nose_cone(self):
        self.rocket.parts.insert(0, NoseCone(colour=self.part_colour, local_part_id=self.rocket.new_part_id))
        self.rocket.new_part_id += 1
    
    def add_decoupler(self):
        self.rocket.parts.append(Decoupler(colour=self.part_colour, local_part_id=self.rocket.new_part_id))
        self.rocket.stages.append([self.rocket.new_part_id])
        self.rocket.new_part_id += 1
      
    def add_engine(self):
        self.rocket.parts.append(Engine(self.rocket.parts[self.get_last_part_in_whitelist([BodyTube, NoseCone])].local_part_id, local_part_id=self.rocket.new_part_id))
        self.rocket.stages.append([self.rocket.new_part_id])
        self.rocket.new_part_id += 1
    
    def add_fins(self):
        self.rocket.parts.append(Fins(self.rocket.parts[self.get_last_part_in_whitelist([BodyTube, NoseCone])].local_part_id, local_part_id=self.rocket.new_part_id))
        self.rocket.new_part_id += 1

    def open_info_panel(self):
        self.info_panel_elements = {
            'title': pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, 10, self.left_panel_ui_container[2], 50), text='Rocket Info', manager=self.ui_manager),
            'wet mass label': pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, 60, self.left_panel_ui_container[2], 50), text='', manager=self.ui_manager),
            'dry mass label': pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, 90, self.left_panel_ui_container[2], 50), text='', manager=self.ui_manager),
            'thrust to weight ratio label': pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, 120, self.left_panel_ui_container[2], 50), text='', manager=self.ui_manager),
            'simulate button': pygame_gui.elements.UIButton(relative_rect=pygame.Rect(10, 640, self.left_panel_ui_container[2]-20, 50), text='Simulate', manager=self.ui_manager),
        }

    def close_info_panel(self):
        for element in self.info_panel_elements.values():
            element.kill()
    
    def update_info_panel(self):
        wet_mass = 0
        dry_mass = 0
        for part in self.rocket.parts:
            dry_mass += part.mass
            wet_mass += part.mass
            if isinstance(part, Engine):
                dry_mass -= part.propellant_mass
        
        thrust_to_weight_ratio = 0
        for part in self.rocket.parts:
            if isinstance(part, Engine):
                thrust_to_weight_ratio = part.average_thrust/(wet_mass*9.81)

        self.info_panel_elements['wet mass label'].set_text(f'Wet Mass: {round(wet_mass, 3)} {self.mass_unit}')
        self.info_panel_elements['dry mass label'].set_text(f'Dry Mass: {round(dry_mass, 3)} {self.mass_unit}')
        self.info_panel_elements['thrust to weight ratio label'].set_text(f'Thrust to Weight Ratio: {round(thrust_to_weight_ratio, 3)}')

    def open_part_editor(self, part):
        self.close_info_panel()

        int_whitelist = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        float_whitelist = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']

        self.part_editor_elements = {}

        self.part_editor_elements.update({'delete part button': pygame_gui.elements.UIButton(relative_rect=pygame.Rect(150, 640, 140, 50), text='Delete', manager=self.ui_manager)})

        if isinstance(part, BodyTube):
            self.part_editor_elements.update({'body tube label': pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, 10, 300, 50), text=f'Edit Body Tube', manager=self.ui_manager)})

            self.add_entry_line('length', part.length, self.length_unit, float_whitelist, 60)
            self.add_entry_line('diameter', part.diameter, self.length_unit, float_whitelist, 120)
            self.add_entry_line('wall thickness', part.wall_thickness, self.length_unit, float_whitelist, 180)

            self.add_entry_line('density', part.density, self.mass_unit, float_whitelist, 520)
            self.add_entry_line('mass', part.mass, self.mass_unit, float_whitelist, 580)

        elif isinstance(part, NoseCone):
            self.part_editor_elements.update({'nose cone label': pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, 10, 300, 50), text=f'Edit Nose Cone', manager=self.ui_manager)})

            self.add_entry_line('length', part.length, self.length_unit, float_whitelist, 60)
            self.add_entry_line('diameter', part.diameter, self.length_unit, float_whitelist, 120)

            self.add_entry_line('density', part.density, self.mass_unit, float_whitelist, 520)
            self.add_entry_line('mass', part.mass, self.mass_unit, float_whitelist, 580)
        
        elif isinstance(part, Decoupler):
            self.part_editor_elements.update({'decoupler label': pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, 10, 300, 50), text=f'Edit Decoupler', manager=self.ui_manager)})

            self.add_entry_line('length', part.length, self.length_unit, float_whitelist, 60)
            self.add_entry_line('diameter', part.diameter, self.length_unit, float_whitelist, 120)

            self.add_entry_line('mass', part.mass, self.mass_unit, float_whitelist, 530)
            self.add_entry_line('stage', str(self.get_part_stage(part)), '', int_whitelist, 590)

        elif isinstance(part, Engine):
            self.part_editor_elements.update({'engine label': pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, 10, 300, 50), text=f'Edit Engine', manager=self.ui_manager)})

            self.add_entry_line('length', part.length, self.length_unit, float_whitelist, 60)
            self.add_entry_line('diameter', part.diameter, self.length_unit, float_whitelist, 120)
            self.add_entry_line('offset', part.offset, self.length_unit, float_whitelist + ['-'], 180)
            self.add_entry_line('average thrust', part.average_thrust, self.force_unit, float_whitelist, 240)
            self.add_entry_line('burn time', part.burn_time, self.time_unit, float_whitelist, 300)

            self.add_entry_line('propellant mass', part.propellant_mass, self.mass_unit, float_whitelist, 470)
            self.add_entry_line('mass', part.mass, self.mass_unit, float_whitelist, 530)
            self.add_entry_line('stage', str(self.get_part_stage(part)), '', int_whitelist, 590)
        
        elif isinstance(part, Fins):
            self.part_editor_elements.update({'fins label': pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, 10, 300, 50), text=f'Edit Fins', manager=self.ui_manager)})

            self.add_entry_line('length', part.length, self.length_unit, float_whitelist, 60)
            self.add_entry_line('width', part.width, self.length_unit, float_whitelist, 120)
            self.add_entry_line('thickness', part.thickness, self.length_unit, float_whitelist, 180)
            self.add_entry_line('offset', part.offset, self.length_unit, float_whitelist + ['-'], 240)

            self.add_entry_line('mass', part.mass, '', float_whitelist, 580)

    def add_entry_line(self, variable, initial_text, unit, allowed_characters, start_y):
        label_start_x = 10
        label_width = 132
        label_height = 50

        entry_start_x = 130
        entry_width = 140
        entry_height = 50

        unit_start_x = 270
        unit_width = 50
        unit_height = 50

        length_limit = 10

        label_object_id = pygame_gui.core.ObjectID(class_id='@text_entry_labels')

        self.part_editor_elements.update({f'{variable} label': pygame_gui.elements.UILabel(relative_rect=pygame.Rect(label_start_x, start_y, label_width, label_height), manager=self.ui_manager, text=f'{variable.capitalize()}:', object_id=label_object_id)})
        self.part_editor_elements.update({f'{variable} entry': pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(entry_start_x, start_y, entry_width, entry_height), manager=self.ui_manager, initial_text=str(initial_text))})
        self.part_editor_elements[f'{variable} entry'].allowed_characters = allowed_characters
        self.part_editor_elements[f'{variable} entry'].length_limit = length_limit
        self.part_editor_elements.update({f'{variable} unit label': pygame_gui.elements.UILabel(relative_rect=pygame.Rect(unit_start_x, start_y, unit_width, unit_height), manager=self.ui_manager, text=unit, object_id=label_object_id)})

    def close_part_editor(self):
        for element in self.part_editor_elements.values():
            element.kill()
        
        self.open_info_panel()


class Simulation():
    def __init__(self, rocket):
        self.alive = True

        self.rocket = rocket

        self.bg_colour = (36, 36, 36)

        self.create_window()
    
    def create_window(self):
        self.get_flight_data()

        self.window_dimensions = (450, 450)
        self.monitor_dimensions = (1920, 1080)
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (3*self.monitor_dimensions[0]/4-self.window_dimensions[0]/2, self.monitor_dimensions[1]/2-self.window_dimensions[1]/2)

        pygame.init()

        self.root = pygame.display.set_mode(self.window_dimensions)
        pygame.display.set_caption('Rocket Simulation')

        self.ui_manager = pygame_gui.UIManager(self.window_dimensions, 'data/themes/simulation_theme.json')

        title_object_id = pygame_gui.core.ObjectID(class_id='@title_labels')

        self.title_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, 10, self.window_dimensions[0], 80), text=f'Simulation Data for {self.rocket.name}', object_id=title_object_id, manager=self.ui_manager)

        self.flight_info_labels = {}

        for key in self.flight_info:
            self.flight_info_labels.update({key: pygame_gui.elements.UILabel(relative_rect=pygame.Rect(0, 85 + list(self.flight_info.keys()).index(key)*50, self.window_dimensions[0], 50), text=f"{key}: {self.flight_info[key]}", manager=self.ui_manager)})

        self.create_graphs()

        self.clock = pygame.time.Clock()

        while self.alive:
            self.time_delta = self.clock.tick(60)/1000

            self.handle_events()

            self.render()
        
        pygame.quit()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                return None

            self.ui_manager.process_events(event)
        
        self.ui_manager.update(self.time_delta)
    
    def render(self):
        plt.draw()
        plt.pause(0.001)

        self.root.fill(self.bg_colour)

        self.ui_manager.draw_ui(self.root)

        pygame.display.update()
    
    def close(self, *args):
        self.alive = False
    
    def get_flight_data(self):
        self.simulator = rocket_simulator.Simulator(self.rocket)
        self.flight_data = self.simulator.simulate()

        burnout_time = self.flight_data['time'][-1]
        for i, fuel in enumerate(self.flight_data['fuel']):
            if fuel == 0:
                burnout_time = self.flight_data['time'][i]
                break
        
        # Convert negative values to postive so an absolute maximum value can be found
        speed = [abs(x) for x in self.flight_data['velocity']]
        proper_acceleration = [abs(x) for x in self.flight_data['acceleration']]
        proper_g_force = [abs(x) for x in self.flight_data['g-force']]

        self.flight_info = {
            'Total Flight Time': f"{round(self.flight_data['time'][-1], 3)} s",
            'Motor Burnout Time': f"{round(burnout_time, 3)} s",
            'Maximum Altitude': f"{round(max(self.flight_data['altitude']), 3)} m",
            'Maximum Speed': f"{round(max(speed), 3)} m/s",
            'Maximum Acceleration': f"{round(max(proper_acceleration), 3)} m/s^2",
            'Maximum G-Force': f"{round(max(proper_g_force), 3)} G's"
        }
    
    def create_graphs(self):
        fig = plt.figure(figsize=(10, 8), tight_layout=True)
        fig.canvas.mpl_connect('close_event', self.close)

        unit = ''
        for i, key in enumerate(self.flight_data):
            if key == 'altitude':
                unit = 'm'
            elif key == 'velocity':
                unit = 'm/s'
            elif key == 'acceleration':
                unit = 'm/s^2'
            elif key == 'g-force':
                unit = 'G\'s'
            elif key == 'thrust' or key == 'drag':
                unit = 'N'
            elif key == 'mass':
                unit = 'kg'
            if key != 'time':
                ax = fig.add_subplot(math.ceil(len(self.flight_data)/2), 2, i)
                ax.plot(self.flight_data['time'], self.flight_data[key])
                ax.set_xlabel('Time (s)')
                ax.set_ylabel(f'{key.capitalize()} ({unit})')
        
        plt.ion()
        plt.show()


class SimulationPlayer():
    def __init__(self, rocket):
        self.alive = True

        self.original_rocket = rocket

        self.step = 0
        self.rocket_angle = math.pi / 2

        self.bg_colour = (36, 36, 36)
        self.part_colour = (255, 255, 255)

        self.create_window()
    
    def create_window(self):
        self.get_flight_data()

        self.window_dimensions = (1500, 700)
        self.monitor_dimensions = (1920, 1080)
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (3*self.monitor_dimensions[0]/4-self.window_dimensions[0]/2, self.monitor_dimensions[1]/2-self.window_dimensions[1]/2)

        pygame.init()

        self.font = pygame.font.Font('data/fonts/Rubik-Regular.ttf', 20)

        self.root = pygame.display.set_mode(self.window_dimensions)
        pygame.display.set_caption('Simulation Player')

        self.ui_manager = pygame_gui.UIManager(self.window_dimensions, 'data/themes/simulation_theme.json')

        label_object_id = pygame_gui.core.ObjectID(class_id='@text_entry_labels')
        play_button_object_id = pygame_gui.core.ObjectID(class_id='@play_buttons')

        self.play_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(700, 550, 100, 100), text='', manager=self.ui_manager, object_id=play_button_object_id)

        self.clock = pygame.time.Clock()

        while self.alive:
            self.time_delta = self.clock.tick(60)/1000

            self.handle_events()

            self.ui_manager.update(self.time_delta)

            self.ui_manager.draw_ui(self.root)

            self.render()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
                return None
            
            self.ui_manager.process_events(event)
    
    def close(self):
        self.alive = False
        pygame.quit()
    
    def render(self):
        self.root.fill(self.bg_colour)

        rocket_renderer.render_rocket_simulation(current_rocket=self.simulator.rocket_at_stage[self.flight_data['stage'][self.step]], flight_data=self.flight_data, time_step=self.step, root=self.root, angle=self.rocket_angle, container=(0, 0, self.window_dimensions[0], self.window_dimensions[1]))

        self.ui_manager.draw_ui(self.root)

        pygame.display.update()

    def get_flight_data(self):
        self.simulator = rocket_simulator.Simulator(self.original_rocket)
        self.flight_data = self.simulator.simulate()

        burnout_time = self.flight_data['time'][-1]
        for i, fuel in enumerate(self.flight_data['fuel']):
            if fuel == 0:
                burnout_time = self.flight_data['time'][i]
                break
        
        # Convert negative values to postive so an absolute maximum value can be found
        speed = [abs(x) for x in self.flight_data['velocity']]
        proper_acceleration = [abs(x) for x in self.flight_data['acceleration']]
        proper_g_force = [abs(x) for x in self.flight_data['g-force']]

        self.flight_info = {
            'Total Flight Time': f"{round(self.flight_data['time'][-1], 3)} s",
            'Motor Burnout Time': f"{round(burnout_time, 3)} s",
            'Maximum Altitude': f"{round(max(self.flight_data['altitude']), 3)} m",
            'Maximum Speed': f"{round(max(speed), 3)} m/s",
            'Maximum Acceleration': f"{round(max(proper_acceleration), 3)} m/s^2",
            'Maximum G-Force': f"{round(max(proper_g_force), 3)} G's"
        }


if __name__ == "__main__":
    MainMenu()