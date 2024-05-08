from math import pi
import random

import unreal

import unreal_engine.utils as utils


class Camera:
    def __init__(self):
        self.focus_distance_section = None
        self.binding = None
        self.actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CineCameraActor, [0., 0., 0.])

    def add_to_level_sequencer(self, level_sequencer, manual_focus=34):
        spawnable_camera_binding = level_sequencer.add_possessable(self.actor)
        transform_section_camera = spawnable_camera_binding.add_track(unreal.MovieScene3DTransformTrack).add_section()
        transform_section_camera.set_start_frame_bounded(0)
        transform_section_camera.set_end_frame_bounded(0)

        camera_cut_track = level_sequencer.add_master_track(unreal.MovieSceneCameraCutTrack)
        camera_cut_section = camera_cut_track.add_section()
        camera_cut_section.set_start_frame(0)
        camera_cut_section.set_end_frame(10)

        camera_binding_id = unreal.MovieSceneObjectBindingID()
        camera_binding_id.set_editor_property("Guid", spawnable_camera_binding.binding_id)
        camera_cut_section.set_editor_property("CameraBindingID", camera_binding_id)

        camera_component = self.actor.get_cine_camera_component()
        filmbacksetting = unreal.CameraFilmbackSettings(sensor_width=24, sensor_height=32)
        camera_component.filmback = filmbacksetting
        camera_component.focus_settings.manual_focus_distance = manual_focus

        camera_component_binding = level_sequencer.add_possessable(camera_component)
        camera_component_binding.set_parent(spawnable_camera_binding)
        focal_length_track = camera_component_binding.add_track(unreal.MovieSceneFloatTrack)
        focal_length_track.set_property_name_and_path('CurrentFocalLength', 'CurrentFocalLength')
        focal_length_section = focal_length_track.add_section()
        focal_length_section.set_start_frame_bounded(0)
        focal_length_section.set_end_frame_bounded(0)

        focus_distance_track = camera_component_binding.add_track(unreal.MovieSceneFloatTrack)
        focus_distance_track.set_property_name_and_path('ManualFocusDistance', 'FocusSettings.ManualFocusDistance')
        focus_distance_section = focus_distance_track.add_section()
        focus_distance_section.set_start_frame_bounded(0)
        focus_distance_section.set_end_frame_bounded(0)
        self.focus_distance_section, self.binding = focus_distance_section, spawnable_camera_binding

    def add_key_transform(self, loc, rot, t):
        utils.add_key_transform(self.binding, loc, rot, t)

    def add_key_random(self, t, dev_theta=pi/15, dev_phi=pi/15, distance=280., offset=[0., 0., 0.]):
        theta = random.uniform(pi/2 - dev_theta, pi/2 + dev_theta)
        phi = random.uniform(pi/2 - dev_phi, pi/2 + dev_phi)

        loc = utils.spherical_coordinates(distance, phi, theta)
        for k in range(3):
            loc[k] += offset[k]
        pitch = phi * 180 / pi - 90
        yaw = theta * 180 / pi - 180
        self.add_key_transform(loc, [0., pitch, yaw], t)
        return ({"location": loc, "rotation": [0., pitch, yaw]})

    def add_key_focus(self, focus_distance, t):
        frame = unreal.FrameNumber(value=t)
        focus_distance_channel = self.focus_distance_section.get_all_channels()[0]
        focus_distance_channel.add_key(frame, focus_distance)

    def change_interpmode(self, mode):
        for track in self.binding.get_tracks():
            param_section = track.get_sections()[0]
            for c in param_section.get_all_channels():
                for key in c.get_keys():
                    key.set_interpolation_mode(mode)