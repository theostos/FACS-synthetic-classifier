import unreal
import random
import unreal_engine.utils as utils
from math import pi

class PointLight:

    def __init__(self):
        self.object = unreal.PointLight(name='pointLight')
        self.actor = unreal.EditorLevelLibrary.spawn_actor_from_object(self.object, [0., 0., 0.])
        self.binding = None

    def add_to_level_sequencer(self, level_sequencer):
        self.binding = level_sequencer.add_possessable(self.actor)
        transform_section = self.binding.add_track(unreal.MovieScene3DTransformTrack).add_section()
        transform_section.set_start_frame_bounded(0)
        transform_section.set_end_frame_bounded(0)

        light_component = self.actor.get_component_by_class(unreal.PointLightComponent)
        self.binding_color = level_sequencer.add_possessable(light_component)
        color_track = self.binding_color.add_track(unreal.MovieSceneColorTrack)
        
        color_track.set_property_name_and_path('Light Color', 'LightColor')

        self.color_section = color_track.add_section()
        self.color_section.set_start_frame_bounded(0)
        self.color_section.set_end_frame_bounded(0)

        self.channel_r = self.color_section.get_channel('Color.R')
        self.channel_g = self.color_section.get_channel('Color.G')
        self.channel_b = self.color_section.get_channel('Color.B')
        self.channel_a = self.color_section.get_channel('Color.A')

    def add_key_transform(self, t, loc, rot):
        assert self.binding, "Not in a level sequencer"
        utils.add_key_transform(self.binding, t, loc, rot)

    def add_key_random(self, t, distance=None, offset=[0., 0., 0.]):
        theta = random.uniform(-pi/3 + pi/2, pi/3 + pi/2)
        phi = random.uniform(pi/8, pi/2)
        if not distance:
            distance = random.uniform(250, 320)
        loc = utils.spherical_coordinates(distance, phi, theta)
        for k in range(3):
            loc[k] += offset[k]
        self.add_key_transform(t, loc, [0., 0., 0.])

        frame = unreal.FrameNumber(value=t)
        self.channel_a.add_key(frame, 1)
        self.channel_r.add_key(frame, random.uniform(0, 1))
        self.channel_g.add_key(frame, random.uniform(0, 1))
        self.channel_b.add_key(frame, random.uniform(0, 1))

        return({"location": loc, "rotation": [0., 0, 0]})

    def change_interpmode(self, mode):
        utils.change_interpmode(self.binding, mode)