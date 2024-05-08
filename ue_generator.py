from pathlib import Path
import os
import sys
from importlib import reload

abs_path = Path(__file__).parent.absolute()
abs_path = os.path.join(abs_path, '')
os.environ["abs_path"] = abs_path

if abs_path not in sys.path:
    sys.path.append(abs_path)

import json
from unreal_engine.utils import prepare_editor
prepare_editor()

import unreal

from unreal_engine.light import PointLight
from unreal_engine.background import load_all_backgrounds
from unreal_engine.camera import Camera
from unreal_engine.level import LevelSequencer
from unreal_engine.metahuman import MetaHuman
from unreal_engine.utils import MetaHumanAssets, linear_interp_keys
from unreal_engine.pose import generate_pose_filter_uniform_from_dict, pose_key
import unreal_engine.random_cubemap

PATH_MAIN = "/media/theo/Backup/data/"
metahuman = MetaHuman(MetaHumanAssets.ada)
# all_backgrounds = load_all_backgrounds()

for iteration in range(1):
    NUM_ANIMATION = 100
    GAP_ANIMATION = 30

    keys_agregation = [{"frame": t, "camera": {}, "metahuman": {}} for t in range((NUM_ANIMATION-1)*(GAP_ANIMATION+1) + 1)]

    # Initialize level sequence

    level = LevelSequencer(f'seq_{iteration}')
    camera = Camera()
    light = PointLight()

    level.add_actor(camera)
    level.add_actor(light)
    level.add_actor(metahuman)
    
    light.add_key_random(0, offset=[0., 0., 180.])

    key_camera = camera.add_key_random(0, distance=40, offset=[0., 0., 143.])

    # Generate animation
    with unreal.ScopedSlowTask(NUM_ANIMATION, "Generate Animation") as slow_task:
        slow_task.make_dialog(can_cancel=True)
        key_metahuman_prec = None
        keys_camera_prec = None
        for k in range(NUM_ANIMATION):
            slow_task.enter_progress_frame(work=1.0, desc=f'Generate Animation {k}/{NUM_ANIMATION}')
            if slow_task.should_cancel():
                break
            frame_time = k*(GAP_ANIMATION + 1)
            key_metahuman = generate_pose_filter_uniform_from_dict(pose_key)
            metahuman.add_key(key_metahuman, frame_time)
            key_camera = camera.add_key_random(frame_time, distance=40, offset=[0., 0., 143.])
            light.add_key_random(frame_time)
            if key_metahuman_prec:
                interp_keys_metahuman = linear_interp_keys(key_metahuman_prec, key_metahuman, GAP_ANIMATION)
                frame_time_prec = (k-1)*(GAP_ANIMATION + 1) + 1
                for t in range(GAP_ANIMATION):
                    keys_agregation[frame_time_prec + t]['metahuman'] = interp_keys_metahuman[t]
                key_metahuman_prec = key_metahuman
            else:
                key_metahuman_prec = key_metahuman
            if keys_camera_prec:
                interp_keys_camera = linear_interp_keys(keys_camera_prec, key_camera, GAP_ANIMATION)
                for t in range(GAP_ANIMATION):
                    keys_agregation[frame_time_prec + t]['camera'] = interp_keys_camera[t]
            else:
                key_camera_prec = key_camera
            keys_agregation[frame_time]['metahuman'] = key_metahuman
            keys_agregation[frame_time]['camera'] = key_camera

    level.update_level_sequencer(0, (NUM_ANIMATION-1)*(GAP_ANIMATION+1) + 1)
    metahuman.change_interpmode(unreal.RichCurveInterpMode.RCIM_LINEAR)
    level.save_level_sequencer()
    level.close_level_sequencer()
    # Save keys
    with open(PATH_MAIN + f"keys_seq_{iteration}.json", 'w', encoding='utf-8') as file:
        json.dump(keys_agregation, file, indent=4)