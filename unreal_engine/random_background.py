import os
import random

import numpy as np
from PIL import Image

import unreal

import unreal_engine.utils as utils

def _generate_random_texture(size, path):
    noise = np.random.rand(size, size, 3) * 255
    image = np.array(noise, dtype=np.uint8)
    img = Image.fromarray(image, 'RGB')
    img.save(path)

def _create_material_with_texture(texture_path, material_name):
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    assetImportData = unreal.AutomatedAssetImportData()
    material_asset_path = f"/Game/Materials/{material_name}"

    assetImportData.destination_path = material_asset_path
    assetImportData.filenames = [texture_path]
    assetImportData.replace_existing = True
    imported_assets = asset_tools.import_assets_automated(assetImportData)
    texture_asset_path = imported_assets[0].get_path_name()

    texture = unreal.EditorAssetLibrary.load_asset(texture_asset_path)
    texture.filter = unreal.TextureFilter.TF_NEAREST
    unreal.EditorAssetLibrary.save_asset(texture_asset_path)

    unreal.EditorLoadingAndSavingUtils.reload_packages([texture.get_package()])

    # Create a new material asset
    material_factory = unreal.MaterialFactoryNew()
    material_asset = asset_tools.create_asset(material_name, material_asset_path, unreal.Material, material_factory)
    
    # Get the material graph
    # material = unreal.MaterialEditingLibrary.get_material_graph(material_asset)
    material = material_asset
    
    # Create a TextureSample node
    texture_node = unreal.MaterialEditingLibrary.create_material_expression(material, unreal.MaterialExpressionTextureSample, -200, 0)
    texture_node.texture = texture
    
    # Connect the texture sample to the material's base color
    unreal.MaterialEditingLibrary.connect_material_property(texture_node, 'RGBA', unreal.MaterialProperty.MP_BASE_COLOR)
    
    # Compile the material
    unreal.MaterialEditingLibrary.recompile_material(material)
    return material_asset.get_path_name()


class RandomBackground():

    _num_instances = 0

    def __init__(self, material_path, location, rotation, scale):
        mesh_asset = unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Plane')

        self.actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, location, rotation)
        self.actor.static_mesh_component.set_static_mesh(mesh_asset)
        self.actor.set_actor_scale3d(scale)

        material = unreal.EditorAssetLibrary.load_asset(material_path)
        self.actor.static_mesh_component.set_material(0, material)

    @classmethod
    def random(cls):
        abs_path = os.environ["abs_path"]
        abs_path_cubemap = os.path.join(abs_path, 'temp/')
        img_path = os.path.join(abs_path_cubemap, f'noise_texture_{cls._num_instances}.png')

        size = random.randint(4,12)
        _generate_random_texture(size, img_path)

        material_path = _create_material_with_texture(img_path, f'NoiseMaterial_{cls._num_instances}')

        location = unreal.Vector(0, -50, 200)  # XYZ coordinates
        rotation = unreal.Rotator(0, 90, -90)  # Pitch, Yaw, Roll
        scale = unreal.Vector(4, 4, 4)  # Uniform scaling
        cls._num_instances += 1
        return cls(material_path, location, rotation, scale)

    def add_key_transform(self, t, loc, rot):
        assert self.binding, "Not in a level sequencer"
        utils.add_key_transform(self.binding, t, loc, rot)

    def add_to_level_sequencer(self, level_sequencer):
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