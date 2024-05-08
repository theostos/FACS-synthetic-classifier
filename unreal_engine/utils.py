from math import cos, sin
from importlib import reload
from functools import partial

import unreal


class MetaHumanAssets:
    ada = '/Game/MetaHumans/ada/BP_ada.BP_ada'

def spherical_coordinates(r, phi, theta):
    x = r * sin(phi) * cos(theta)
    y = r * sin(phi) * sin(theta)
    z = r * cos(phi)
    return([x, y, z])

def add_key_transform(binding, loc, rot, t):
    """
    channels[0], channels[1], channels[2] = pos(x,y,z)
    channels[3], channels[4], channels[5] = rot(x,y,z)
    """
    frame = unreal.FrameNumber(value=t)
    transform_track = binding.find_tracks_by_exact_type(unreal.MovieScene3DTransformTrack)[0]
    transform_section = transform_track.get_sections()[0]
    channels = transform_section.get_all_channels()
    for i in range(3):
        channels[i].add_key(frame, loc[i])
        channels[i + 3].add_key(frame, rot[i])

def prepare_editor():
    import unreal_engine.background as background
    import unreal_engine.camera as camera
    import unreal_engine.level as level
    import unreal_engine.light as light
    import unreal_engine.metahuman as metahuman
    import unreal_engine.utils as utils
    import unreal_engine.random_cubemap as random_cubemap
    reload(background)
    reload(camera)
    reload(level)
    reload(light)
    reload(metahuman)
    reload(utils)
    reload(random_cubemap)

def linear_interp_keys(old_keys, new_keys, gap_num):
    interpolation_virtual = lambda y0, y1, t: (1-t/(gap_num+1))*y0 + t/(gap_num+1)*y1
    res = [{} for t in range(gap_num)]
    for key in old_keys:
        old_key = old_keys[key]
        new_key = new_keys[key]
        if isinstance(old_key, list):
            num_e = len(old_key)
            for t in range(1, gap_num + 1):
                res[t-1][key] = [0]*num_e
            for k in range(num_e):
                interpolation = partial(interpolation_virtual, old_key[k], new_key[k])
                for t in range(1, gap_num + 1):
                    val_interp = interpolation(t)
                    res[t-1][key][k] = val_interp
        elif isinstance(old_key, float):
            interpolation = partial(interpolation_virtual, old_key, new_key)
            for t in range(1, gap_num + 1):
                val_interp = interpolation(t)
                res[t-1][key] = val_interp
    return res


def change_interpmode(binding, mode):
    for track in binding.get_tracks():
        param_section = track.get_sections()[0]
        for c in param_section.get_all_channels():
            for key in c.get_keys():
                key.set_interpolation_mode(mode)