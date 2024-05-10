import os
import time
import math

import pyautogui
import cv2 as cv
import numpy as np
from PIL import ImageGrab


def take_screenshot(resize_full_hd=True):
    idx_screen = int(os.environ['idx_screen'])
    num_screen = int(os.environ['num_screen'])

    screenshot = ImageGrab.grab()
    screenshot = np.array(screenshot)
    screenshot = cv.cvtColor(screenshot, cv.COLOR_RGB2BGR)
    h, w, _ = screenshot.shape
    screenshot = screenshot[:,w//num_screen * idx_screen:w//num_screen * (idx_screen + 1),:]
    if resize_full_hd:
        h, w, _ = screenshot.shape
        gcd_w_h = math.gcd(h,w)
        num, denum = w//gcd_w_h, h//gcd_w_h
        assert num==16 and denum==9, "Wrong ratio, please fix the script"
        screenshot = cv.resize(screenshot, (1920, 1080))
    return(screenshot)


def save_screenshot(filename):
    screenshot = take_screenshot()
    cv.imwrite(filename, screenshot) 


def compute_scale(res_ref=(1920, 1080)):
    screenshot = take_screenshot(resize_full_hd=False)
    _, w, _ = screenshot.shape
    return w/res_ref[0]

def find_img(img, threshold=0.95):
    screenshot = take_screenshot()
    res = cv.matchTemplate(screenshot, img, cv.TM_CCOEFF_NORMED)
    ys, xs = np.where(res >= threshold)
    # print(np.max(res))
    if len(xs) > 0:
        x = xs[0] + img.shape[1]//2
        y = ys[0] + img.shape[0]//2
        # print(f"Detection threshold {np.max(res)}")
        return (x, y)
    raise Exception('Image not found')


def find_bool_img(img, threshold=0.95):
    try:
        find_img(img, threshold=threshold)
        return True
    except Exception as e:
        return False

def move_to_img(img, delay=0.1, scale=1.0):
    res = find_img(img)
    moveTo(res[0], res[1], delay, scale=scale)


def click_img(img, threshold=0.95, scale=1.0):
    res = find_img(img, threshold=threshold)
    click(x=res[0], y=res[1], scale=scale)


def wait_for_img(img, timeout=60., threshold=0.95):
    for _ in range(int(timeout * 10)):
        time.sleep(0.1)
        res = find_bool_img(img, threshold=threshold)
        if res:
            return True
    raise Exception('Image not found')

def wait_and_click_img(img, timeout=60., threshold=0.95, scale=1.0):
    wait_for_img(img, timeout=timeout, threshold=threshold)
    click_img(img, scale=scale)

def rescale(x, y, scale):
    return int(x*scale), int(y*scale)

def click(x, y, scale=1.):
    new_x, new_y = rescale(x, y, scale)
    pyautogui.click(new_x, new_y)

def moveTo(x, y, delay, scale=1.):
    new_x, new_y = rescale(x, y, scale)
    pyautogui.moveTo(new_x, new_y, delay)

def dragTo(x, y, delay, button='left', scale=1.):
    new_x, new_y = rescale(x, y, scale)
    pyautogui.dragTo(new_x, new_y, delay, button=button)

def drag(x, y, delay, button='left', scale=1.):
    new_x, new_y = rescale(x, y, scale)
    pyautogui.drag(new_x, new_y, delay, button=button)

def scroll(length):
    pyautogui.scroll(length)

def press(cmd):
    pyautogui.press(cmd)

def hotkey(*cmd):
    pyautogui.hotkey(*cmd)