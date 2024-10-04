# BlendMSFS Plugin: Usage Guide

## Download and Installation

1. Go to the [BlendMSFS GitHub Releases page](https://github.com/username/BlendMSFS/releases) (replace with actual URL)
2. Download the latest release ZIP file
3. In Blender: Edit > Preferences > Add-ons > Install > Select the ZIP file
4. Enable the add-on by checking the box next to "Import-Export: BlendMSFS"

## Basic Usage

1. Open the sidebar in the 3D Viewport (press 'N')
2. Find the "MSFS Export" tab
3. Set the "ModelLib Path" to your MSFS project's ModelLib folder

### Exporting a Model

1. Organize your model into a Blender collection
2. In the MSFS Export panel:
   - Select your collection
   - Choose LOD levels (0-3)
   - Set texture resolution and format
   - Toggle XML generation
   - Adjust scale if needed
3. Click "Export MSFS Model"

Your model will be exported to a new folder in the ModelLib directory.

## Tips

- Ensure proper UV mapping
- Use Principled BSDF shader for materials
- Name collections and objects clearly
- Check scale (MSFS uses meters)

## Troubleshooting

- Verify all paths are correct
- Ensure textures are properly linked
- For complex models, consider manual LOD creation