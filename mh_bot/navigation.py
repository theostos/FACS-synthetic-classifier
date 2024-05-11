import random
import time
import os
from math import pi, cos, sin

import yaml
import cv2 as cv

import mh_bot.utils as utils

def load_folder(path):
    nav_dict = {}
    for name in os.listdir(path):
        path_name = os.path.join(path, name)
        if os.path.isdir(path_name) and name[0]!="_":
            nav_dict[name] = {}
            for subname in os.listdir(path_name):
                full_path = os.path.join(path_name, subname)
                subname = subname.split('.')[0]
                if '_' in subname:
                    subname_0, subname_1 = subname.split('_')
                    if subname_0 not in nav_dict[name]:
                        nav_dict[name][subname_0] = {}
                    nav_dict[name][subname_0][subname_1] = cv.imread(full_path)
                else:
                    nav_dict[name][subname] = cv.imread(full_path)
        elif name.endswith('.yaml'):
            subname = name.split('.')[0]
            subname_0, subname_1 = subname.split('_')
            if subname_0 not in nav_dict:
                nav_dict[subname_0] = {}
            with open(path_name, 'r', encoding='utf-8') as yaml_file:
                nav_dict[subname_0][subname_1] = yaml.safe_load(yaml_file)
        elif name.startswith('enable'):
            nav_dict['enable'] = cv.imread(path_name)
    return nav_dict

def _load_generic(path, menu):
    nav_editor = {menu: load_folder(path)}
    submenus_path = os.path.join(path, '_submenus')
    nav_editor[menu]['submenus'] = {}
    for submenu in os.listdir(submenus_path):
        submenu_path = os.path.join(submenus_path, submenu)
        nav_editor[menu]['submenus'][submenu] = load_folder(submenu_path)
    return nav_editor

class Navigation():

    def __init__(self, path='data/mh_bot/'):
        self.nav_dict = {}
        for folder in os.listdir(path):
            path_folder = os.path.join(path, folder)
            self.nav_dict.update(_load_generic(path_folder, folder))

        self.interrupt = False
        self.current_menu = ''
        self.current_submenu = ''
        self.last_start = time.time() + 3600
        self.characters = list(self.nav_dict['main']['submenus']['creation']['characters'])
        self.scale = utils.compute_scale()
        self.characters.sort()
        self.force_restart()

    def force_restart(self):
        utils.hotkey('ctrl', 'r')
        time.sleep(1)
        if utils.find_bool_img(self.nav_dict['general']['buttons']['leave']):
            utils.wait_and_click_img(self.nav_dict['general']['buttons']['leave'], scale=self.scale)

        img_start = self.nav_dict['general']['buttons']['start']
        utils.wait_and_click_img(img_start, timeout=30., scale=self.scale)

        img_launch = self.nav_dict['general']['buttons']['launch']
        utils.wait_and_click_img(img_launch, timeout=30., scale=self.scale)

        img_active = self.nav_dict['general']['buttons']['active']
        utils.wait_for_img(img_active, timeout=300)

        x, y = self.nav_dict['general']['keypoints']["fullscreen"]["fullscreen"]
        utils.click(x, y, scale=self.scale)
    
        self.last_start = time.time()
        self.wait_stable_state()
        
    
    @property
    def submenu(self):
        return self.nav_dict[self.current_menu]['submenus'][self.current_submenu]
    
    def update_current_state(self):
        for entry, value in self.nav_dict.items():
            if utils.find_bool_img(value['enable']):
                self.current_menu = entry
                submenus = self.nav_dict[self.current_menu]['submenus']
                for entry, submenu in submenus.items():
                    if utils.find_bool_img(submenu['enable']):
                        self.current_submenu = entry
                        return True
        raise Exception('Current state uncertainty')
    
    def wait_for_state(self, menu, submenu, timeout=30.):
        start = time.time()
        while time.time() - start < timeout:
            try:
                self.update_current_state()
                if self.current_menu == menu and self.current_submenu == submenu:
                    return True
            except Exception as e:
                pass
        raise Exception('Current state uncertainty')
        
    def wait_stable_state(self, timeout=30.):
        start = time.time()
        while time.time() - start < timeout:
            try:
                self.update_current_state()
                return True
            except Exception as e:
                pass
        raise Exception('Current state uncertainty')

    def _move_to_menu(self, menu):
        if self.current_menu == menu:
            return True
        else:
            move_menu_img = self.nav_dict[self.current_menu]['move'][menu]
            utils.wait_and_click_img(move_menu_img, timeout=60., scale=self.scale)
            wait_img = self.nav_dict[menu]['enable']
            utils.wait_for_img(wait_img)
            self.current_menu = menu

    def _move_to_submenu(self, submenu):
        if self.current_submenu == submenu:
            return True
        else:
            move_submenu_img = self.nav_dict[self.current_menu]['move'][submenu]
            utils.wait_and_click_img(move_submenu_img, timeout=60., scale=self.scale)
            wait_img = self.nav_dict[self.current_menu]['submenus'][submenu]['enable']
            utils.wait_for_img(wait_img)
            self.current_submenu = submenu

    def move_to_target(self, menu, submenu):
        self._move_to_menu(menu)
        self._move_to_submenu(submenu)

    def scroll_target(self, target_cat, target_name, scroll_speed=1, timeout=60., delay=0.5):
        scroll_ref = self.submenu[target_cat]["scroll"]
        utils.move_to_img(scroll_ref, scale=self.scale)
        target = self.submenu[target_cat][target_name]
        start = time.time()
        while not utils.find_bool_img(target):
            utils.scroll(-scroll_speed)
            time.sleep(delay)
            delta = time.time() - start
            if delta > timeout:
                raise Exception('Target not found')

    def click_target(self, target_cat, target_name, timeout=60., delay=0.5):
        img = self.submenu[target_cat][target_name]
        start = time.time()
        while not utils.find_bool_img(img):
            time.sleep(delay)
            delta = time.time() - start
            if delta > timeout:
                raise Exception('Target not found')
        utils.click_img(img, scale=self.scale)
    
    def click_keypoint(self, target_cat, target_name):
        x, y = self.submenu['keypoints'][target_cat][target_name]
        utils.click(x, y, scale=self.scale)

    def drag_img_to_keypoint(self, img, keypoint):
        x0, y0 = utils.find_img(img)
        x1, y1 = keypoint
        utils.moveTo(x0, y0, 0.5, scale=self.scale)
        time.sleep(0.5)
        utils.dragTo(x1, y1, 2, button='left', scale=self.scale)
        time.sleep(0.5)

    def toggle_button(self, button, toggle):
        button_on = self.submenu['buttons'][button]['on']
        button_off = self.submenu['buttons'][button]['off']
        if toggle:
            if not utils.find_bool_img(button_on):
                utils.wait_and_click_img(button_off, scale=self.scale)
        else:
            if not utils.find_bool_img(button_off):
                utils.wait_and_click_img(button_on, scale=self.scale)

    def generate_random_character(self, character_base):
        if (time.time() - self.last_start)/60 > 50:
            self.force_restart()

        if not self.interrupt:
            self.move_to_target("main", "creation")

            self.scroll_target("characters", self.characters[0], scroll_speed=-100)

            self.scroll_target("characters", character_base)
            self.click_target("characters", character_base)
            utils.wait_and_click_img(self.submenu['buttons']["selected"]["on"], scale=self.scale)
        else:
            self.move_to_target("main", "archive")
            self.click_keypoint("character", "character0")
            utils.wait_and_click_img(self.submenu['buttons']["edit"]["on"], scale=self.scale)
        self.wait_for_state("editor", "base")

        self.move_to_target("editor", "skin")
        x0, y0 = self.submenu['keypoints']['texture']['min']
        x1, y1 = self.submenu['keypoints']['texture']['max']
        x = x0 + random.uniform(0,1)*(x1-x0)
        y = y0 + random.uniform(0,1)*(y1-y0)
        utils.click(x, y, scale=self.scale)

        self.move_to_target("editor", "proportions")
        self.click_keypoint("headsize", "size")
        time.sleep(1)
        utils.press('del')
        utils.press('del')
        utils.press('del')
        utils.press('del')
        utils.press('backspace')
        utils.press('backspace')
        utils.press('backspace')
        utils.press('backspace')

        utils.press('0')
        utils.press('enter')
        self.click_keypoint("size", "average")
        self.click_keypoint("corpulency", "medium_0")
        time.sleep(3)
        self.move_to_target("editor", "blend")

        characters_minus_base = self.characters.copy()
        characters_minus_base.remove(character_base)
        names = sorted(random.sample(characters_minus_base, k=3))
        keypoints = self.submenu['keypoints']['diagram']
        for name, keypoint in zip(names, keypoints.values()):
            img = self.submenu["characters"][name]
            self.scroll_target("characters", name)
            self.drag_img_to_keypoint(img, keypoint)
        

        utils.press('6')
        self.toggle_button('hidehair', True)
        self.toggle_button('blend', True)
        utils.press('1')
        time.sleep(3)

        for (x, y) in self.submenu["keypoints"]["blend"].values():
            dist_r = 250 + 100*random.uniform(0, 1)
            utils.moveTo(x, y, 0.5, scale=self.scale)
            angle = random.random() * 2 * pi
            delta_x = dist_r * cos(angle)
            delta_y = dist_r * sin(angle)
            utils.drag(delta_x, delta_y, 0.5, button='left', scale=self.scale)
            time.sleep(0.5)

        self.move_to_target("editor", "eyes")
        keypoint_name = random.choice(list(self.submenu["keypoints"]['eyes'].keys()))
        self.click_keypoint("eyes", keypoint_name)

        self.move_to_target("editor", "head")
        panel_down = bool(random.getrandbits(1))
        if panel_down:
            keypoint_cat = "headdown"
            scroll_ref = self.submenu["items"]["scroll"]
            utils.move_to_img(scroll_ref, scale=self.scale)
            utils.scroll(-300)
            time.sleep(1)
            utils.scroll(-300)
        else:
            keypoint_cat = "headup"
        keypoints = self.submenu['keypoints'][keypoint_cat]
        keypoint_name = random.choice(list(keypoints.keys()))
        self.click_keypoint(keypoint_cat, keypoint_name)

        self.move_to_target("editor", "eyebrows")
        keypoint_name = random.choice(list(self.submenu["keypoints"]['eyebrows'].keys()))
        self.click_keypoint("eyebrows", keypoint_name)

        self.move_to_target("editor", "eyelashes")
        keypoint_name = random.choice(list(self.submenu["keypoints"]['eyelashes'].keys()))
        self.click_keypoint("eyelashes", keypoint_name)

        rand_pilosity = random.uniform(0,1)

        if rand_pilosity > 0.5:
            if rand_pilosity > 0.5 + 1/6.:
                self.move_to_target("editor", "mustache")
                keypoint_name = random.choice(list(self.submenu["keypoints"]['mustache'].keys()))
                self.click_keypoint("mustache", keypoint_name)
            if rand_pilosity > 0.5 + 2/6. or (rand_pilosity > 0.5 and rand_pilosity < 0.5 + 1/6):
                self.move_to_target("editor", "beard")
                keypoint_name = random.choice(list(self.submenu["keypoints"]['beard'].keys()))
                self.click_keypoint("beard", keypoint_name)
        time.sleep(2)
        self.interrupt = False
        self.move_to_target("main", "creation")
        self.scroll_target("characters", self.characters[0], scroll_speed=-100)
