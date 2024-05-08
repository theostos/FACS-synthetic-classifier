import unreal
import unreal_engine.utils as utils

class LevelSequencer:

    def __init__(self, name):
        self.frame_end_num = 0
        self.level_sequencer = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
        if not self.level_sequencer:
            self.asset_level_sequence = unreal.load_asset('/Game/python_level')
            unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(self.asset_level_sequence)
            self.level_sequencer = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
        unreal.EditorAssetLibrary.duplicate_loaded_asset(self.level_sequencer, f'/Game/export_sequence/{name}')
        unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
        self.asset_level_sequence = unreal.load_asset(f'/Game/export_sequence/{name}')
        unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(self.asset_level_sequence)
        self.level_sequencer = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
        # self.__clean_sequencer()

    def __clean_sequencer(self):
        for binding in self.level_sequencer.get_bindings():
            binding.remove()
        for track in self.level_sequencer.get_master_tracks():
            self.level_sequencer.remove_master_track(track)

    def save_level_sequencer(self):
        unreal.EditorAssetLibrary.save_loaded_asset(self.level_sequencer)

    def close_level_sequencer(self):
        unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()

    def clean_editor(self):
        self.__clean_sequencer()
        for actor in unreal.EditorActorSubsystem().get_all_level_actors():
            unreal.EditorActorSubsystem().destroy_actor(actor)
        unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()

    def update_level_sequencer(self, min_frame, max_frame):
        camera_cut_track = self.level_sequencer.find_master_tracks_by_type(unreal.MovieSceneCameraCutTrack)[0]
        camera_cut_section = camera_cut_track.get_sections()[0]
        camera_cut_section.set_start_frame(min_frame)
        camera_cut_section.set_end_frame(max_frame)
        self.level_sequencer.set_playback_start(min_frame)
        self.level_sequencer.set_playback_end(max_frame)

    def add_actor(self, actor):
        actor.add_to_level_sequencer(self.level_sequencer)

    def export_animation_fbx(self, min_frame, maxframe, metahuman, filename):
        self.update_level_sequencer(min_frame, maxframe)
        editor_system = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        world = editor_system.get_editor_world()

        newAnim = unreal.AnimSequence()
        anim_export_options = unreal.AnimSeqExportOption()
        anim_export_options.export_transforms = True
        anim_export_options.evaluate_all_skeletal_mesh_components = True
        if metahuman.component_face.skeletal_mesh:
            newAnim.set_preview_skeletal_mesh(metahuman.component_face.skeletal_mesh)
        unreal.SequencerTools.export_anim_sequence(world, self.level_sequencer, newAnim, anim_export_options, metahuman.binding_face, False)
        
        export_options = unreal.FbxExportOption()
        export_options.ascii = False
        export_options.collision = False
        export_options.export_local_time = False
        export_options.export_morph_targets = False
        export_options.export_preview_mesh = True
        export_options.fbx_export_compatibility = unreal.FbxExportCompatibility.FBX_2013
        export_options.force_front_x_axis = False
        export_options.level_of_detail = False
        export_options.map_skeletal_motion_to_root = True
        export_options.vertex_color = False

        export_task = unreal.AssetExportTask()
        export_task.set_editor_property("object", newAnim)
        export_task.set_editor_property("automated", True)
        export_task.set_editor_property("options", export_options)
        export_task.set_editor_property("filename", filename)
        export_task.set_editor_property("exporter", unreal.AnimSequenceExporterFBX())
        unreal.Exporter.run_asset_export_task(export_task)

    # see Engine/Plugins/MovieScene/SequencerScripting/Content/Python/sequencer_examples.py
    def export_video(self, min_frame, maxframe, path, callback):
        self.update_level_sequencer(min_frame, maxframe)
        capture_settings = unreal.AutomatedLevelSequenceCapture()
        capture_settings.set_image_capture_protocol_type(unreal.load_class(None, "/Script/MovieSceneCapture.ImageSequenceProtocol_JPG"))
        capture_settings.level_sequence_asset = unreal.SoftObjectPath(self.level_sequencer.get_path_name())

        capture_settings.settings.overwrite_existing = True
        capture_settings.settings.resolution.res_x = 240
        capture_settings.settings.resolution.res_y = 320
        capture_settings.settings.cinematic_mode = True
        capture_settings.settings.allow_movement = True

        # capture_settings.settings.use_path_tracer = True
        capture_settings.settings.enable_texture_streaming = False

        capture_settings.warm_up_frame_count = 10
        capture_settings.delay_before_shot_warm_up = 10
        capture_settings.settings.output_directory = unreal.DirectoryPath(path)
        unreal.SequencerTools.render_movie(capture_settings, callback)
