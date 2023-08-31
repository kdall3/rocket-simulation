import numpy as np


def check_point_in_box(point, rects):
    if len(np.array(rects).shape) == 1:  # If there is 1 rect
        box = ((rects[0], rects[1]), (rects[0] + rects[2], rects[1] + rects[3]))

        if (point[0] >= box[0][0] and point[0] <= box[1][0]) and (point[1] >= box[0][1] and point[1] <= box[1][1]):
            return True
        else:
            return False
    else:  # If there are multiple rects
        for rect in rects:
            box = ((rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]))

            if (point[0] >= box[0][0] and point[0] <= box[1][0]) and (point[1] >= box[0][1] and point[1] <= box[1][1]):
                return True


def get_box_centre(box):
    return (box[0] + box[2]/2, box[1] + box[3]/2)
