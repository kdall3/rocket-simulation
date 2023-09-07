import rocket_parts
import math
import time

g = 9.81

def get_drag_coefficient(part):
    if isinstance(part, rocket_parts.BodyTube):
        angle = 90
        return 0.0112 * angle + 0.162
    elif isinstance(part, rocket_parts.NoseCone):
        angle = math.atan((part.diameter/2)/part.length)
        return 0.0112 * angle + 0.162
    elif isinstance(part, rocket_parts.Fins):
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
            if isinstance(part, rocket_parts.Engine):
                self.engine = part
            elif isinstance(part, rocket_parts.NoseCone) and self.nose is None:
                self.nose = part
                self.drag_coefficient_area_total += get_drag_coefficient(part) * math.pi * (part.diameter/2)**2
            elif isinstance(part, rocket_parts.BodyTube) and self.nose is None:
                self.nose = part
                self.drag_coefficient_area_total += get_drag_coefficient(part) * math.pi * (part.diameter/2)**2
            elif isinstance(part, rocket_parts.Fins):
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

        for part in self.rocket.parts:
            self.mass += part.mass

        self.flight_data = {
            'time': [],
            'altitude': [],
            'velocity': [],
            'acceleration': [],
            'g-force': [],
            'thrust': [],
            'drag': [],
            'fuel': [],
            'mass': []
        }
    
    def simulate(self):
        t1 = time.perf_counter()
        while True:
            self.step()

            self.update_flight_data()

            if self.altitude < self.altitude_cutoff:
                print(f"Simulation finished in {time.perf_counter() - t1} seconds")
                return self.flight_data

            self.time += self.time_increment
    
    def step(self):
        fuel_decrease = self.time_increment / self.engine.burn_time
        if self.fuel < fuel_decrease and self.fuel > 0:
            self.thrust = self.engine.average_thrust * self.fuel/fuel_decrease
            self.fuel = 0

            self.mass -= self.fuel * self.engine.propellant_mass
        elif self.fuel <= 0:
            self.thrust = 0
            self.fuel = 0
        else:
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
