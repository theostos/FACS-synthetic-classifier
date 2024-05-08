import os

import numpy as np
from PIL import Image

import unreal

def generate_random_texture():
    size = 6  # Size of the cubemap face
    abs_path = os.environ["abs_path"]
    abs_path_cubemap = os.path.join(abs_path, 'temp/')
    noise = np.random.rand(size, size, 3) * 255
    image = np.array(noise, dtype=np.uint8)
    img = Image.fromarray(image, 'RGB')
    img_path = os.path.join(abs_path_cubemap, 'noise_texture.png')
    img.save(img_path)

def create_material_with_texture():
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    # Load the texture
    abs_path = os.environ["abs_path"]
    abs_path = os.path.join(abs_path, 'temp/')
    abs_path_texture = os.path.join(abs_path, 'noise_texture.png')

    assetImportData = unreal.AutomatedAssetImportData()

    assetImportData.destination_path = "/Game/Materials/NoiseMaterial"
    assetImportData.filenames = [abs_path_texture]
    asset_tools.import_assets_automated(assetImportData)

    texture = unreal.EditorAssetLibrary.load_asset("/Game/Materials/NoiseMaterial/noise_texture")
    texture.filter = unreal.TextureFilter.TF_NEAREST
    unreal.EditorAssetLibrary.save_asset("/Game/Materials/NoiseMaterial/noise_texture")

    unreal.EditorLoadingAndSavingUtils.reload_packages([texture.get_package()])
    # Create a new material asset
    material_factory = unreal.MaterialFactoryNew()
    material_asset_path = '/Game/Materials/NoiseMaterial'

    material_asset = asset_tools.create_asset("NoiseMaterial", material_asset_path, unreal.Material, material_factory)
    
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


def spawn_procedural_plane_mesh(mesh_path, material_path, location, rotation, scale):
    mesh_asset = unreal.EditorAssetLibrary.load_asset(mesh_path)

    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, location, rotation)
    actor.static_mesh_component.set_static_mesh(mesh_asset)
    actor.set_actor_scale3d(scale)

    material = unreal.EditorAssetLibrary.load_asset(material_path)
    
    # Apply the material
    if isinstance(actor, unreal.StaticMeshActor):
        actor.static_mesh_component.set_material(0, material)
    return actor

generate_random_texture()
create_material_with_texture()
location = unreal.Vector(0, -50, 200)  # XYZ coordinates
rotation = unreal.Rotator(0, 90, -90)  # Pitch, Yaw, Roll
scale = unreal.Vector(4, 4, 4)  # Uniform scaling
material_path = '/Game/Materials/NoiseMaterial/NoiseMaterial'  # Path to the noise material created earlier

spawn_procedural_plane_mesh('/Engine/BasicShapes/Plane', material_path, location, rotation, scale)
