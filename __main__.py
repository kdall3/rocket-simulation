import pygame
import pygame_gui

import editor
import rocket_loader


class MainMenu():
    def __init__(self):
        self.alive = True

        self.bg_colour = (36, 36, 36)

        self.create_window()
    
    def create_window(self):
        pygame.init()

        self.window_dimensions = (700, 700)
        self.root = pygame.display.set_mode(self.window_dimensions)
        pygame.display.set_caption('Rocket Simulation')

        self.ui_manager = pygame_gui.UIManager(self.window_dimensions, 'data/themes/menu_theme.json')

        title_object_id = pygame_gui.core.ObjectID(class_id='@title_labels')

        title_width = 400

        button_width = 400
        button_height = 100

        self.title_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(self.window_dimensions[0]/2-title_width/2, 20, title_width, 100), text='Rocket Simulator', object_id=title_object_id, manager=self.ui_manager)

        self.create_rocket_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(self.window_dimensions[0]/2-button_width/2, 140, button_width, button_height), text='Create New Rocket', manager=self.ui_manager)
        self.edit_rocket_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(self.window_dimensions[0]/2-button_width/2, 260, button_width, button_height), text='Edit Saved Rocket', manager=self.ui_manager)

        self.create_simulation_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(self.window_dimensions[0]/2-button_width/2, 400, button_width, button_height), text='Create New Simulation', manager=self.ui_manager)
        self.edit_simulation_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(self.window_dimensions[0]/2-button_width/2, 520, button_width, button_height), text='Edit Saved Simulation', manager=self.ui_manager)

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
            
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.create_rocket_button:
                    self.create_rocket()
                elif event.ui_element == self.edit_rocket_button:
                    self.edit_rocket()
                elif event.ui_element == self.edit_rocket_button:
                    self.create_simulation()
                elif event.ui_element == self.edit_rocket_button:
                    self.edit_simulation()
        
            self.ui_manager.process_events(event)
        
        self.ui_manager.update(self.time_delta)
    
    def render(self):
        self.root.fill(self.bg_colour)

        self.ui_manager.draw_ui(self.root)

        pygame.display.update()

    def create_rocket(self):
        self.alive = False

        editor.run()

    def edit_rocket(self):
        rocket_loader.run('main menu', 'editor')
    
    def create_simulation(self):
        pass

    def edit_simulation(self):
        pass


if __name__ == "__main__":
    MainMenu()