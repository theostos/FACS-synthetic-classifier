import random

import unreal

from config.config import background_config

def load_all_backgrounds():
    result = []
    cubemap_list = background_config['cubemap_list']
    for cubemap_name in cubemap_list:
        background = Background(cubemap_name=cubemap_name)
        result.append(background)
    return(result)

class Background:
    def __init__(self, cubemap_name=None):
        self.config = background_config
        self.asset = unreal.load_asset(self.config['asset_path'])
        self.actor = unreal.EditorLevelLibrary.spawn_actor_from_object(self.asset, [0., 0., 0.])
        if cubemap_name:
            cubemap = unreal.load_asset(cubemap_name)
            self.actor.set_editor_property("cubemap", cubemap)

    def random_background(self):
        cubemap = unreal.load_asset(random.choice(self.config['cubemap_list']))
        self.actor.set_editor_property("cubemap", cubemap)

    def random_intensity(self):
        value = random.uniform(0.0,3.0)
        self.actor.set_editor_property("intensity", value)

    def add_to_level(self, level_sequencer):
        self.binding = level_sequencer.add_possessable(self.actor)
        visibility_section = self.binding.add_track(unreal.MovieSceneVisibilityTrack).add_section()
        visibility_section.set_start_frame_bounded(0)
        visibility_section.set_end_frame_bounded(0)

    def add_key_visibility(self, t, toggle):
        frame = unreal.FrameNumber(value=t)
        track = self.binding.find_tracks_by_exact_type(unreal.MovieSceneVisibilityTrack)[0]
        section = track.get_sections()[0]
        channel = section.get_all_channels()[0]
        channel.add_key(frame, toggle)