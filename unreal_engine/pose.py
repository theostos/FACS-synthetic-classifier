import json
import random
import os

from unreal_engine.key import key_uniform, key_zero

abs_path = os.environ["abs_path"]
PATH_EMOTION = abs_path + 'data/pose/pose_emotion.json'
PATH_VISEME = abs_path + 'data/pose/pose_viseme.json'
PATH_CLUSTERS = abs_path + 'data/clusters/'

lower_c_path = os.path.join(PATH_CLUSTERS, 'lower_c.json')
lower_l_path = os.path.join(PATH_CLUSTERS, 'lower_l.json')
lower_r_path = os.path.join(PATH_CLUSTERS, 'lower_r.json')

upper_c_path = os.path.join(PATH_CLUSTERS, 'upper_c.json')
upper_l_path = os.path.join(PATH_CLUSTERS, 'upper_l.json')
upper_r_path = os.path.join(PATH_CLUSTERS, 'upper_r.json')

with open(lower_c_path, 'r', encoding='utf-8') as file:
    lower_c = json.load(file)
with open(lower_l_path, 'r', encoding='utf-8') as file:
    lower_l = json.load(file)
with open(lower_r_path, 'r', encoding='utf-8') as file:
    lower_r = json.load(file)

with open(upper_c_path, 'r', encoding='utf-8') as file:
    upper_c = json.load(file)
with open(upper_l_path, 'r', encoding='utf-8') as file:
    upper_l = json.load(file)
with open(upper_r_path, 'r', encoding='utf-8') as file:
    upper_r = json.load(file)

pose_key = {}

pose_key.update(lower_c)
pose_key.update(lower_r)
pose_key.update(lower_l)
pose_key.update(upper_c)
pose_key.update(upper_r)
pose_key.update(upper_l)

pose_emotion = list(json.load(open(PATH_EMOTION, 'r', encoding='utf-8')).values())
pose_viseme = json.load(open(PATH_VISEME, 'r', encoding='utf-8'))


def generate_pose_filter_uniform_from_dict(dict_key):
    new_control = list(dict_key.keys()).copy()
    num_elements = random.randrange(len(new_control))

    random.shuffle(new_control)
    new_control_rand = new_control[:num_elements]
    new_control_zero = new_control[num_elements:]

    new_pose = {}
    for control in new_control_rand:
        new_pose[control] = key_uniform(control)
    for control in new_control_zero:
        new_pose[control] = key_zero(control)
    return(new_pose)