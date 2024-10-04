import bpy
import os
import uuid
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import numpy as np
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty, PointerProperty
from bpy.types import Operator, Panel, PropertyGroup

bl_info = {
    "name": "BlendMSFS",
    "author": "Scorcher",
    "version": (0, 9),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > MSFS Export",
    "description": "Export models for Microsoft Flight Simulator",
    "category": "Import-Export",
}

class MSFSExportSettings(PropertyGroup):
    modellib_path: StringProperty(
        name="ModelLib Path",
        description="Path to ModelLib folder",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
    )
    collection: PointerProperty(
        name="Collection to Export",
        type=bpy.types.Collection,
        description="Select the collection to export"
    )
    lod_levels: EnumProperty(
        name="LOD Levels",
        description="Number of LOD levels to generate",
        items=[
            ('0', "No LOD", "Export without LOD"),
            ('1', "1 Level", "Generate 1 LOD level"),
            ('2', "2 Levels", "Generate 2 LOD levels"),
            ('3', "3 Levels", "Generate 3 LOD levels"),
        ],
        default='1'
    )
    texture_resolution: EnumProperty(
        name="Texture Resolution",
        description="Resolution of exported textures",
        items=[
            ('1024', "1024x1024", "Export textures at 1024x1024"),
            ('2048', "2048x2048", "Export textures at 2048x2048"),
            ('4096', "4096x4096", "Export textures at 4096x4096"),
        ],
        default='2048'
    )
    generate_xml: BoolProperty(
        name="Generate XML",
        description="Generate MSFS XML file",
        default=True
    )
    scale_factor: FloatProperty(
        name="Scale Factor",
        description="Scale factor for export",
        default=1.0,
        min=0.01,
        max=100.0
    )

def generate_xml(filepath, settings):
    root = ET.Element("ModelInfo")
    root.set("version", "1.1")
    root.set("guid", "{" + str(uuid.uuid4()) + "}")

    # LODS
    lods = ET.SubElement(root, "LODS")
    for i in range(int(settings.lod_levels) + 1):
        lod = ET.SubElement(lods, "LOD")
        lod.set("ModelFile", f"{os.path.splitext(os.path.basename(filepath))[0]}_LOD{i}.gltf")
        lod.set("minSize", str(i * 1000))  # Example LOD distance

    # Pretty print XML
    xml_string = ET.tostring(root, 'utf-8')
    pretty_xml = minidom.parseString(xml_string).toprettyxml(indent="  ")

    xml_filepath = os.path.splitext(filepath)[0] + '.xml'
    with open(xml_filepath, "w") as f:
        f.write(pretty_xml)

    return xml_filepath

class MSFS_PT_export_panel(Panel):
    bl_label = "MSFS Export"
    bl_idname = "MSFS_PT_export_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MSFS Export"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.msfs_export_settings

        layout.prop(settings, "modellib_path")
        layout.prop(settings, "collection")
        layout.prop(settings, "lod_levels")
        layout.prop(settings, "texture_resolution")
        layout.prop(settings, "generate_xml")
        layout.prop(settings, "scale_factor")

        layout.separator()
        layout.operator("export.msfs_model")

class MSFS_OT_export(Operator):
    bl_idname = "export.msfs_model"
    bl_label = "Export MSFS Model"
    bl_description = "Export the model to MSFS format"

    def execute(self, context):
        settings = context.scene.msfs_export_settings
        
        if not settings.modellib_path:
            self.report({'ERROR'}, "ModelLib path is not set")
            return {'CANCELLED'}
        
        if not settings.collection:
            self.report({'ERROR'}, "No collection selected for export")
            return {'CANCELLED'}
        
        # Update image paths
        self.update_image_paths(context)
        
        # Use the collection name for the export
        collection_name = settings.collection.name
        
        # Create a folder for this collection inside ModelLib
        collection_folder = os.path.join(settings.modellib_path, collection_name)
        os.makedirs(collection_folder, exist_ok=True)
        
        # Create texture folder inside the ModelLib directory
        texture_folder = os.path.join(settings.modellib_path, "texture")
        os.makedirs(texture_folder, exist_ok=True)
        
        # Set the active collection
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[settings.collection.name]
        
        # Select only the objects in the chosen collection
        bpy.ops.object.select_all(action='DESELECT')
        for obj in settings.collection.objects:
            obj.select_set(True)
        
        # Export GLTF for each LOD level
        for i in range(int(settings.lod_levels) + 1):
            lod_filepath = os.path.join(collection_folder, f"{collection_name}_LOD{i}.gltf")
            bpy.ops.export_scene.gltf(
                filepath=lod_filepath,
                use_selection=True,
                export_format='GLTF_SEPARATE',
                export_texture_dir=texture_folder,
                export_texcoords=True,
                export_normals=True,
                export_draco_mesh_compression_enable=False,
                export_materials='EXPORT',
                export_apply=True,
                export_animations=False,
                export_lights=False,
                export_cameras=False
            )
            
            # Apply LOD simplification (placeholder)
            self.apply_lod_simplification(context, i)

        # Generate XML
        if settings.generate_xml:
            xml_path = generate_xml(os.path.join(collection_folder, f"{collection_name}.gltf"), settings)
            self.report({'INFO'}, f"XML file generated at {xml_path}")

        # Process and export textures
        self.process_textures(context, texture_folder, settings)

        # Clean up non-PNG files in texture folder
        self.cleanup_texture_folder(texture_folder)

        self.report({'INFO'}, f"MSFS Model '{collection_name}' exported successfully to {collection_folder}")
        return {'FINISHED'}
    
    def update_image_paths(self, context):

        def find_file(name, path):
            for root, dirs, files in os.walk(path):
                if name in files:
                    return os.path.join(root, name)
            return None

        # Get the directory of the current blend file
        blend_file_path = bpy.data.filepath
        blend_file_dir = os.path.dirname(blend_file_path)

        updated_count = 0
        for image in bpy.data.images:
            if not os.path.exists(image.filepath):
                # Get just the filename
                image_filename = os.path.basename(image.filepath)
                
                # Try to find the correct part of the path
                path_parts = image.filepath.split(os.sep)
                if 'Downloads' in path_parts:
                    downloads_index = path_parts.index('Downloads')
                    correct_path = os.path.join(*path_parts[:downloads_index+3])  # Include 'Downloads' and the next two folders
                    
                    # Search for the file in the correct directory and its subdirectories
                    new_path = find_file(image_filename, correct_path)
                    
                    if new_path:
                        image.filepath = new_path
                        updated_count += 1
                        print(f"Updated path for {image.name}: {new_path}")
                    else:
                        print(f"Could not find file for {image.name} in {correct_path}")
                else:
                    print(f"Could not determine correct path for {image.name}")

        self.report({'INFO'}, f"Updated {updated_count} image paths")

    def apply_lod_simplification(self, context, lod_level):
        # Placeholder for LOD simplification
        pass

    def process_textures(self, context, texture_folder, settings):
        for material in bpy.data.materials:
            if material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        image = node.image
                        texture_path = os.path.join(texture_folder, self.get_valid_filename(image.name))
                        
                        print(f"\nProcessing texture: {image.name}")
                        print(f"Texture node: {node.name}")
                        print(f"Material: {material.name}")
                        print(f"Image filepath: {image.filepath}")
                        print(f"Image size: {image.size}")
                        print(f"Image channels: {image.channels}")
                        
                        try:
                            # Check if the image file exists
                            if not os.path.exists(image.filepath):
                                raise FileNotFoundError(f"Image file not found: {image.filepath}")
                            
                            # Resize and export texture as PNG
                            self.resize_and_export_image(image, int(settings.texture_resolution), texture_path)
                        except Exception as e:
                            error_message = f"Failed to process texture {image.name}: {str(e)}"
                            self.report({'WARNING'}, error_message)
                            print(error_message)
                            
                            # Try to reload the image
                            print("Attempting to reload the image...")
                            image.reload()
                            print(f"After reload - Image size: {image.size}, channels: {image.channels}")
                            
                            if image.size[0] == 0 or image.size[1] == 0:
                                print("Image still has invalid dimensions after reload.")
                            else:
                                print("Image reloaded successfully. Retrying resize operation...")
                                try:
                                    self.resize_and_export_image(image, int(settings.texture_resolution), texture_path)
                                except Exception as retry_error:
                                    print(f"Retry failed: {str(retry_error)}")

    def resize_and_export_image(self, original_image, target_size, output_path):

        # Print diagnostic information
        print(f"Processing image: {original_image.name}")
        print(f"Original filepath: {original_image.filepath}")
        print(f"Original size: {original_image.size}")
        print(f"Original channels: {original_image.channels}")

        # Ensure the image is loaded
        if original_image.packed_file:
            print("Image is packed, unpacking...")
            original_image.unpack(method='USE_ORIGINAL')
        original_image.reload()

        # Check if the image has valid dimensions and pixels
        if original_image.size[0] == 0 or original_image.size[1] == 0:
            raise ValueError(f"Image '{original_image.name}' has invalid dimensions: {original_image.size}")

        if len(original_image.pixels) == 0:
            raise ValueError(f"Image '{original_image.name}' has no pixel data")

        # Get original image dimensions and pixels
        width, height = original_image.size
        channels = original_image.channels
        pixels = np.array(original_image.pixels[:])

        if pixels.size == 0:
            raise ValueError(f"Image '{original_image.name}' has empty pixel data")

        pixels = pixels.reshape((height, width, channels))

        # Create a new image with the target size
        resized_image = bpy.data.images.new(
            name=f"{original_image.name}_resized", 
            width=target_size, 
            height=target_size
        )

        # Perform resize using numpy
        x = np.linspace(0, width - 1, target_size)
        y = np.linspace(0, height - 1, target_size)
        x_indices = np.clip(x.astype(np.int32), 0, width - 1)
        y_indices = np.clip(y.astype(np.int32), 0, height - 1)
        resized_pixels = pixels[np.ix_(y_indices, x_indices)]

        # Flatten the resized pixels and assign to the new image
        resized_image.pixels = resized_pixels.flatten()

        # Save the resized image
        resized_image.file_format = 'PNG'
        resized_image.filepath_raw = output_path
        resized_image.save()

        # Remove the temporary resized image from memory
        bpy.data.images.remove(resized_image)

        print(f"Resized image saved to: {output_path}")

    def cleanup_texture_folder(self, texture_folder):
        for filename in os.listdir(texture_folder):
            if not filename.lower().endswith('.png'):
                file_path = os.path.join(texture_folder, filename)
                os.remove(file_path)

    def get_valid_filename(self, name):
        return "".join(c for c in name if c.isalnum() or c in (' ', '.', '_')).rstrip()

classes = (
    MSFSExportSettings,
    MSFS_PT_export_panel,
    MSFS_OT_export,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.msfs_export_settings = bpy.props.PointerProperty(type=MSFSExportSettings)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.msfs_export_settings

if __name__ == "__main__":
    register()