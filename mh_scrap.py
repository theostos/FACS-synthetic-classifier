import os
import time

import mh_bot.utils as utils
from mh_bot.navigation import Navigation

def take_screenshot():
    while True:
        os.system('clear')
        filename = input('Picture ?')
        utils.save_screenshot(f'{filename}.png')
        input('\n End! Clear ?')

def test_detection():
    nav = Navigation()
    while True:
        nav.wait_stable_state(timeout=30.)
        os.system('clear')
        print(nav.current_menu)
        print(nav.current_submenu)
        input('\n End! Clear ?')
        

def test_scrolling():
    nav = Navigation()
    while True:
        nav.wait_stable_state(timeout=30.)
        os.system('clear')
        print(nav.current_menu, nav.current_submenu)
        print("Category:")
        print("\n\t".join(nav.submenu.keys()))
        target_cat = input('Target category?\n')
        if target_cat in nav.submenu:
            print("\n".join(nav.submenu[target_cat].keys()))
            target_name = input('Target name?\n')
            nav.scroll_target(target_cat, target_name)
        input('\n End! Clear ?')

def test_keypoints():
    nav = Navigation()
    nav.wait_stable_state(timeout=30.)
    print("Keypoint:")
    print("\n\t".join(nav.submenu['keypoints'].keys()))
    keypoint_name = input('Keypoint name ?\n')
    for entry, (x, y) in nav.submenu['keypoints'][keypoint_name].items():
        print(entry)
        utils.moveTo(x, y, 0.5, scale=nav.scale)
        input('next ?')
# test_scrolling()
# test_keypoints()

nav = Navigation()

for _ in range(10):
    for name in nav.characters:
        print("NEW CHARACTER")
        print(f"base character: {name}")
        for _ in range(3):
            start = time.time()
            try:
                nav.generate_random_character(name)
                print(f"Elapsed time: {time.time() - start}")
                break
            except Exception as e:
                print(e)
                print("RETRY")
                nav.interrupt = True
                nav.force_restart()