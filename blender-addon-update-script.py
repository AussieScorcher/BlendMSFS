import os
import shutil
import sys

def update_addon():
    # Set paths
    blender_version = "4.2"
    addon_name = "BlendMSFS"  # Changed to match the expected name
    
    # Source directory (where your development files are)
    src_dir = os.path.join(os.getcwd(), "src")
    
    # Destination directory (Blender's addon directory)
    if sys.platform == "win32":
        dest_dir = os.path.join(os.getenv('APPDATA'), "Blender Foundation", "Blender", blender_version, "scripts", "addons", addon_name)
    elif sys.platform == "darwin":  # macOS
        dest_dir = os.path.expanduser(f"~/Library/Application Support/Blender/{blender_version}/scripts/addons/{addon_name}")
    else:  # Linux and other Unix
        dest_dir = os.path.expanduser(f"~/.config/blender/{blender_version}/scripts/addons/{addon_name}")

    # Ensure the destination directory exists
    os.makedirs(dest_dir, exist_ok=True)

    # Copy files
    for file in os.listdir(src_dir):
        if file.endswith('.py'):
            src_file = os.path.join(src_dir, file)
            dest_file = os.path.join(dest_dir, file)
            shutil.copy2(src_file, dest_file)
            print(f"Copied {file} to {dest_dir}")

    print("Addon update complete!")

if __name__ == "__main__":
    update_addon()