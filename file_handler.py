import os
import pickle

rockets_path = 'data/saved/rockets'

def save_rocket(rocket, name):
    path = os.path.join(rockets_path, name) + '.dat'

    with open(path, 'wb') as f:
        pickle.dump(rocket, f)

def get_all_saved_rockets():
    rockets = []
    for filename in os.listdir(rockets_path):
            filename = os.path.join(rockets_path, filename)
            if os.path.isfile(filename):
                with open(filename, 'rb') as f:
                    rockets.append(pickle.load(f))
    
    return rockets

def delete_rocket(rocket):
    path = os.path.join(rockets_path, rocket.name) + '.dat'

    os.remove(path)