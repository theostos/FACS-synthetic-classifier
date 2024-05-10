import os

import cv2

NUM_STEP_X = 3
NUM_STEP_Y = 7

img_path = 'hair_1.png'
img = cv2.imread(img_path)

xstart, ystart = 260, 260
jump_x = 127
jump_y = 127

rect_x = 50
rect_y = 50


for i in range(NUM_STEP_Y):
    for j in range(NUM_STEP_X):
        center_x, center_y = xstart + j*jump_x, ystart + i*jump_y
        x0, y0 = center_x - rect_x, center_y - rect_y
        x1, y1 = center_x + rect_x, center_y + rect_y
        cv2.imwrite(f"export/item_{j + i*NUM_STEP_X+ 18}.png", img[y0:y1, x0:x1])