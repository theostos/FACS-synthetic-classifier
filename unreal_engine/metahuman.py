import json
import os

import unreal

import unreal_engine.utils as utils

class CtrlRigAssets:
    body_rig = unreal.load_asset('/Game/MetaHumans/Common/Common/MetaHuman_ControlRig.MetaHuman_ControlRig')
    face_rig_simple = unreal.load_asset('/Game/MetaHumans/Common/Face/simple_face_CtrlRig.simple_face_CtrlRig')
    face_rig = unreal.load_asset('/Game/MetaHumans/Common/Face/Face_ControlBoard_CtrlRig.Face_ControlBoard_CtrlRig')


class MetaHuman:

    def __init__(self, path_asset):
        self.control_rig_face = None
        self.control_rig_body = None
        self.asset = unreal.load_asset(path_asset)
        self.actor = unreal.EditorLevelLibrary.spawn_actor_from_object(self.asset, [0., 0., 0.])
        abs_path = os.environ["abs_path"]
        with open(abs_path + 'data/control_rig/control_type.json', 'r') as file:
            self.control_json = json.load(file)

    def add_to_level_sequencer(self, level_sequencer):
        editor_system = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        world = editor_system.get_editor_world()
        level_sequencer.add_possessable(self.actor)
        binding_face = None
        # for unknown reason, adding control rig to body is causing unreal editor to crash
        # binding_body = None
        component_body = None
        component_face = None
        control_rig_face = None
        control_rig_body = None

        for component in self.actor.root_component.get_children_components(True):
            if component.get_name() == "Face":
                binding_face = level_sequencer.add_possessable(component)
                component_face = component
            if component.get_name() == "Body":
                # binding_body = level_sequence.add_possessable(component)
                component_body = component
        unreal.ControlRigSequencerLibrary.find_or_create_control_rig_track(world, level_sequencer, CtrlRigAssets.face_rig.get_control_rig_class(), binding_face)
        # unreal.ControlRigSequencerLibrary.find_or_create_control_rig_track(self.world, self.level_sequence, CtrlRigAssets.body_rig.get_control_rig_class(), self.binding_body)
        rig_proxies = unreal.ControlRigSequencerLibrary.get_control_rigs(level_sequencer)
        for rig in rig_proxies:
            if rig.control_rig.get_name() == "Face_ControlBoard_CtrlRig":
                control_rig_face = rig.control_rig
            if rig.control_rig.get_name() == "MetaHuman_ControlRig":
                control_rig_body = rig.control_rig
        self.control_rig_face = control_rig_face
        self.binding_face = binding_face
        self.component_face = component_face
        self.control_rig_body = control_rig_body
        self.component_body =  component_body

    def remove_hair(self):
        root = self.actor.root_component
        components = root.get_children_components(True)
        for c in components:
            if "GroomComponent" in c.get_full_name():
                c.destroy_component(c)

    def add_key(self, t, key):
        track = self.binding_face.get_tracks()[0]
        frame = unreal.FrameNumber(value=t)
        for channel in track.get_sections()[0].get_all_channels():
            channel_name = str(channel.channel_name)
            value = None
            if '.X' in channel_name:
                channel_name = channel_name.split('.')[0]
                if channel_name in key:
                    value = key[channel_name][0]
            elif '.Y' in channel_name:
                channel_name = channel_name.split('.')[0]
                if channel_name in key:
                    value = key[channel_name][1]
            else:
                if channel_name in key:
                    value = key[channel_name]
            if isinstance(channel, unreal.MovieSceneScriptingFloatChannel) and value:
                _ = channel.add_key(frame, value, interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
    
    def change_interpmode(self, mode):
        utils.change_interpmode(self.binding_face, mode)
