from rocket_parts import *
import math
import time

g = 9.81

def get_drag_coefficient(part):
    if isinstance(part, BodyTube):
        angle = 90
        return 0.0112 * angle + 0.162
    elif isinstance(part, NoseCone):
        angle = math.atan((part.diameter/2)/part.length)
        return 0.0112 * angle + 0.162
    elif isinstance(part, Fins):
        return 0.075

def get_drag_force(drag_coefficient, air_density, velocity, area):
    return 0.5 * drag_coefficient * air_density * velocity**2 * area

class Simulator():
    def __init__(self, rocket, air_density=1.225, time_increment=0.01, altitude_cutoff=-10):
        self.rocket = rocket
        self.air_density = air_density
        self.time_increment = time_increment
        self.altitude_cutoff = altitude_cutoff

        self.engine = None
        self.nose = None
        self.fins = []

        self.drag_coefficient_area_total = 0 # Total of all drag coefficients multiplied by their respective areas

        for part in self.rocket.parts:
            if isinstance(part, Engine) and part.local_part_id in rocket.stages[0]:
                self.engine = part
            elif isinstance(part, NoseCone) and self.nose is None:
                self.nose = part
                self.drag_coefficient_area_total += get_drag_coefficient(part) * math.pi * (part.diameter/2)**2
            elif isinstance(part, BodyTube) and self.nose is None:
                self.nose = part
                self.drag_coefficient_area_total += get_drag_coefficient(part) * math.pi * (part.diameter/2)**2
            elif isinstance(part, Fins):
                self.fins.append(part)
                self.drag_coefficient_area_total += get_drag_coefficient(part) * part.width * part.thickness

        self.time = 0
        self.altitude = 0
        self.velocity = 0
        self.acceleration = 0
        self.g_force = 0
        self.thrust = self.engine.average_thrust
        self.drag = 0
        self.fuel = 1
        self.mass = 0

        self.stage = 0
        self.max_stage = len(rocket.stages) - 1

        self.parts_to_part_ids = {}
        for part in self.rocket.parts:
            self.mass += part.mass
            self.parts_to_part_ids.update({part.local_part_id:part})

        self.rocket_at_stage = []

        self.flight_data = {
            'time': [],
            'altitude': [],
            'velocity': [],
            'acceleration': [],
            'g-force': [],
            'thrust': [],
            'drag': [],
            'fuel': [],
            'mass': [],
            'stage': []
        }
    
    def simulate(self):
        self.rocket_at_stage.append(self.rocket)

        while True:
            self.step()

            self.update_flight_data()

            if self.altitude < self.altitude_cutoff:
                return self.flight_data

            self.time += self.time_increment
    
    def step(self):
        self.thrust = 0
        if self.engine is not None:
            fuel_decrease = self.time_increment / self.engine.burn_time
            if self.fuel < fuel_decrease and self.fuel > 0: # Engine burning partway during the time step
                self.thrust = self.engine.average_thrust * self.fuel/fuel_decrease
                self.fuel = 0

                self.mass -= self.fuel * self.engine.propellant_mass

            elif self.fuel <= 0: # Engine not burning at all during the time step
                self.thrust = 0
                self.fuel = 0 

                if self.stage != self.max_stage:  # STAGE
                    self.stage += 1
                    for part_id in self.rocket.stages[self.stage]:
                        part_in_stage = self.parts_to_part_ids[part_id]
                        if isinstance(part_in_stage, Decoupler):
                            reached_decoupler = False
                            for part in self.rocket.parts:
                                if check_part_type(part, [BodyTube, NoseCone, Decoupler]):
                                    if part.local_part_id == part_in_stage.local_part_id:
                                        reached_decoupler = True
                                    elif reached_decoupler:
                                        children = get_children(part, self.rocket)
                                        self.rocket.parts.remove(part)

                                        for child in children:
                                            self.rocket.parts.remove(child)
                            
                            self.mass = 0
                            for part in self.rocket.parts:
                                self.mass += part.mass
                        elif isinstance(part_in_stage, Engine):
                            self.engine = part_in_stage
                            self.fuel = 1
                            self.thrust = self.engine.average_thrust
                
                    self.rocket_at_stage.append(self.rocket)

            else: # Engine burning all the way during the time step
                self.thrust = self.engine.average_thrust
                self.fuel -= fuel_decrease

                self.mass -= fuel_decrease * self.engine.propellant_mass

        if self.velocity >= 0:
            self.drag = 0.5 * self.air_density * self.velocity**2 * self.drag_coefficient_area_total * -1
        else:
            self.drag = 0.5 * self.air_density * self.velocity**2 * self.drag_coefficient_area_total

        self.acceleration = (self.thrust + self.drag) / self.mass - g
        self.velocity += self.acceleration * self.time_increment
        self.altitude += self.velocity * self.time_increment

        self.g_force = self.acceleration / g

        if self.acceleration > 1000:
            print(self.thrust, self.drag, self.mass, self.acceleration)

    def update_flight_data(self):
        self.flight_data['time'].append(self.time)
        self.flight_data['altitude'].append(self.altitude)
        self.flight_data['velocity'].append(self.velocity)
        self.flight_data['acceleration'].append(self.acceleration)
        self.flight_data['g-force'].append(self.g_force)
        self.flight_data['thrust'].append(self.thrust)
        self.flight_data['drag'].append(self.drag)
        self.flight_data['fuel'].append(self.fuel)
        self.flight_data['mass'].append(self.mass)
        self.flight_data['stage'].append(self.stage)
