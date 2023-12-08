import numpy as np
import math


def pygame_box_to_poly(box):
    return [[box[0], box[1]], [box[0] + box[2], box[1]], [box[0] + box[2], box[1] + box[3]], [box[0], box[1] + box[3]]]


def get_poly_bounding_box(poly):
    x = [i[0] for i in poly]
    y = [i[1] for i in poly]
    return ((min(x), min(y)), (max(x), max(y)))


def get_centroid_poly(poly):
    A = 0

    for i, _ in enumerate(poly):
        u = poly[i-1]
        v = poly[i]
        A += u[0] * v[1] - v[0] * u[1]
    A = A/2

    centroid = np.array([0.0, 0.0])
    for i, _ in enumerate(poly):
        u = poly[i-1]
        v = poly[i]
        centroid[0] += (u[0] + v[0]) * (u[0] * v[1] - v[0] * u[1])
        centroid[1] += (u[1] + v[1]) * (u[0] * v[1] - v[0] * u[1])
    centroid[0] = centroid[0] / (6 * A)
    centroid[1] = centroid[1] / (6 * A)

    return centroid


def check_point_in_box(point, rects):
    if len(np.array(rects).shape) == 1:  # If there is 1 rect
        box = ((rects[0], rects[1]), (rects[0] + rects[2], rects[1] + rects[3]))

        if (point[0] >= box[0][0] and point[0] <= box[1][0]) and (point[1] >= box[0][1] and point[1] <= box[1][1]):
            return True
        elif (point[0] <= box[0][0] and point[0] >= box[1][0]) and (point[1] <= box[0][1] and point[1] >= box[1][1]):
            return True
        else:
            return False

    else:  # If there are multiple rects
        for rect in rects:
            box = ((rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]))

            if (point[0] >= box[0][0] and point[0] <= box[1][0]) and (point[1] >= box[0][1] and point[1] <= box[1][1]):
                return True
            elif (point[0] <= box[0][0] and point[0] >= box[1][0]) and (point[1] <= box[0][1] and point[1] >= box[1][1]):
                return True
            else:
                return False


def check_point_in_poly(point, poly):
    # Rough check
    bounding_box = get_poly_bounding_box(poly)
    if not (point[0] > bounding_box[0][0] and point[0] < bounding_box[1][0]) and (point[1] > bounding_box[0][1] and point[0] < bounding_box[1][1]):
        return False
    
    # Ray casting algorithm
    intersections = 0
    for i, _ in enumerate(poly):
        p1 = poly[i-1]
        p2 = poly[i]
        if not ((p1[1] > point[1] and p2[1] > point[1]) or (p1[1] < point[1] and p2[1] < point[1])):
            s = p1[0] + (p2[0]-p1[0]) * ((point[1]-p1[1])/(p2[1]-p1[1]))
            if point[0] > s:
                intersections += 1

    if intersections % 2 == 0:
        return False
    else:
        return True


def get_box_centre(box):
    return (box[0] + box[2]/2, box[1] + box[3]/2)


def rotate_poly(poly, centre, angle):  # Angle measured in radians
    poly = np.array([np.array(vertex) for vertex in poly])
    centre = np.array([float(centre[0]), float(centre[1])])
    R = np.array(((np.cos(angle), -np.sin(angle)), (np.sin(angle), np.cos(angle))))

    poly = np.dot((poly - centre), R) + centre

    return [list(vertex) for vertex in poly]
