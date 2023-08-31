import pygame
import pygame_gui

import __main__
import editor
import file_handler
import geometry


class RocketLoader():
    def __init__(self, last_window, target_window):
        self.last_window = last_window
        self.target_window = target_window

        self.alive = True

        self.bg_colour = (36, 36, 36)

        self.rocket_name_font = pygame.font.Font('data/fonts/Rubik-Regular.ttf', 20)

        self.rockets = file_handler.get_all_saved_rockets()

        self.create_window()
    
    def create_window(self):
        pygame.init()

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

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 or event.button == 3:
                    mouse_pos = pygame.mouse.get_pos()
                    for i, rect in enumerate(self.rect_list):
                        if rect != None:
                            if geometry.check_point_in_box(mouse_pos, rect):
                                self.selected_index = i

            elif event.type == pygame.MOUSEWHEEL:
                self.scroll_position += self.scroll_increment*event.y*-1
                if self.scroll_position < 0:
                    self.scroll_position = 0
                elif len(self.rockets)*self.listing_difference < self.rocket_list_container[3]:
                    self.scroll_position = 0
                elif self.scroll_position > len(self.rockets)*self.listing_difference - self.rocket_list_container[3]:
                    self.scroll_position = len(self.rockets)*self.listing_difference - self.rocket_list_container[3]
            
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.load_button:
                    self.load_selected_rocket()
                elif event.ui_element == self.delete_button:
                    self.delete_selected_rocket()
            
            self.ui_manager.process_events(event)
        
        self.ui_manager.update(self.time_delta)

    def render(self):
        self.root.fill(self.bg_colour)

        self.rect_list = []

        for i, rocket in enumerate(self.rockets):
            unlocked_start_y = (i+1)*self.listing_difference - self.scroll_position
            start_y = unlocked_start_y
            height = self.listing_height

            if start_y > self.rocket_list_container[1] - height and start_y < self.rocket_list_container[1] + self.rocket_list_container[3]:
                if start_y < self.rocket_list_container[1]:
                    height = height - (self.rocket_list_container[1] - start_y)
                    start_y = self.rocket_list_container[1]
                elif start_y + height > self.rocket_list_container[1] + self.rocket_list_container[3]:
                    height = height - (start_y + height - (self.rocket_list_container[1] + self.rocket_list_container[3]))
                
                rect = (self.rocket_list_container[0], start_y, self.rocket_list_container[2], height)

                pygame.draw.rect(self.root, (69, 73, 78), rect, border_radius=3)
                if i == self.selected_index and rect[3] >= 10: # Have to check if the height is greater than 10 because otherwise the border radius will be too big
                    pygame.draw.rect(self.root, (255, 255, 255), rect, border_radius=3, width=3)

                name_surface = self.rocket_name_font.render(rocket.name, True, (255, 255, 255))
                self.root.blit(name_surface, (self.rocket_list_container[0]+10, unlocked_start_y+10))

                self.rect_list.append(rect)
            else:
                self.rect_list.append(None)

        pygame.draw.rect(self.root, self.bg_colour, (0, 0, self.window_dimensions[0], self.rocket_list_container[1]))
        pygame.draw.rect(self.root, self.bg_colour, (0, self.rocket_list_container[1]+self.rocket_list_container[3], self.window_dimensions[0], self.window_dimensions[1] - (self.rocket_list_container[1]+self.rocket_list_container[3])))

        self.ui_manager.draw_ui(self.root)

        pygame.display.update()
    
    def back_to_last_window(self):
        self.alive = False

        if self.last_window == 'main menu':
            __main__.MainMenu()
        elif self.last_window == 'editor':
            editor.run()
        else:
            raise Exception('Invalid last window')
    
    def delete_selected_rocket(self):
        if self.selected_index != None:
            file_handler.delete_rocket(self.rockets[self.selected_index])
            self.rockets = file_handler.get_all_saved_rockets()
            self.selected_index = None
    
    def load_selected_rocket(self):
        if self.selected_index != None:
            if self.target_window == 'editor':
                self.alive = False
                editor.run(self.rockets[self.selected_index])
            else:
                raise Exception('Invalid target window')

def run(last_window, target_window):
    RocketLoader(last_window, target_window)