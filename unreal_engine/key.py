import random
import unreal

from config.config import control_json

def clip(key_name, value):
    if control_json[key_name]['type'] == 'float':
        new_value = max(value, control_json[key_name]['min'])
        new_value = min(value, control_json[key_name]['max'])
        return(new_value)
    elif control_json[key_name]['type'] == 'vec2':
        new_value_x = max(value[0], control_json[key_name]['min_x'])
        new_value_x = min(new_value_x, control_json[key_name]['max_x'])

        new_value_y = max(value[1], control_json[key_name]['min_y'])
        new_value_y = min(new_value_y, control_json[key_name]['max_y'])
        return([new_value_x, new_value_y])

def key_zero(key_name):
    if control_json[key_name]['type'] == 'float_switch':
        return(0.0000001)
    elif control_json[key_name]['type'] == 'float':
        return(0.0000001)
    elif control_json[key_name]['type'] == 'vec2':
        return([0.0000001, 0.0000001])

def key_min(key_name):
    if control_json[key_name]['type'] == 'float':
        return(control_json[key_name]['min'])
    elif control_json[key_name]['type'] == 'vec2':
        return([control_json[key_name]['min_x'], control_json[key_name]['min_y']])

def key_max(key_name):
    if control_json[key_name]['type'] == 'float':
        return(control_json[key_name]['max'])
    elif control_json[key_name]['type'] == 'vec2':
        return([control_json[key_name]['max_x'], control_json[key_name]['max_y']])

def key_gauss(key_name, mu=0.0, sigma=0.3):
    if control_json[key_name]['type'] == 'float':
        value = random.gauss(mu, sigma)
        value = clip(key_name, value)
        return(value)
    elif control_json[key_name]['type'] == 'vec2':
        value_x = random.gauss(mu, sigma)
        value_y = random.gauss(mu, sigma)
        vec = clip(key_name, [value_x, value_y])
        return(vec)

def key_uniform(key_name):
    if control_json[key_name]['type'] == 'float':
        min_bound = control_json[key_name]['min']
        max_bound = control_json[key_name]['max']
        value = random.uniform(min_bound, max_bound)
        return(value)
    elif control_json[key_name]['type'] == 'vec2':
        min_bound_x = control_json[key_name]['min_x']
        max_bound_x = control_json[key_name]['max_x']

        min_bound_y = control_json[key_name]['min_y']
        max_bound_y = control_json[key_name]['max_y']

        value_x = random.uniform(min_bound_x, max_bound_x)
        value_y = random.uniform(min_bound_y, max_bound_y)

        return([value_x, value_y])

def get_key_at_t(level_sequence, face_rig, frame):
    new_key = {"frame": frame, "metahuman": {}}
    frame = unreal.FrameNumber(frame)
    for control in control_json.keys():
        if control_json[control]['type'] == 'vec2':
            vec2 = unreal.ControlRigSequencerLibrary.get_local_control_rig_vector2d(level_sequence, face_rig, control, frame)
            value = [vec2.x, vec2.y]
            new_key["metahuman"][control] = value
        elif control_json[control]['type'] == 'float':
            value = unreal.ControlRigSequencerLibrary.get_local_control_rig_float(level_sequence, face_rig, control, frame)
            new_key["metahuman"][control] = value
    return(new_key)

def get_all_keys(level_sequence, face_rig, frame_start, frame_end):
    res = []
    for k in range(frame_start, frame_end + 1):
        new_key = get_key_at_t(level_sequence, face_rig, k)
        res.append(new_key)
    return(res)
