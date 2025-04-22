# Stylized Hair and Stubble for Blender


A Blender addon that makes it easy to create stylized short hair and stubble on any mesh, with complete control over color, density, and appearance.

## Features

- 💇‍♂️ Create realistic or stylized hair and stubble with a few clicks
- 🎨 Independent color control with standard Blender color pickers
- 🔍 Live updates as you adjust settings
- 👴 Salt and pepper grey percentage controls for both hair and stubble
- 🔄 Compatible with Blender 4.0+ (tested on 4.4)
- 🎭 Transparency control for the underlying mesh
- 🚀 Optimized for animation performance
- 🛠️ Works with GBH or other hair curve conversion tools

## Installation

1. Download the `stylized_hair_stubble.py` file
2. Open Blender and go to Edit > Preferences
3. Select the "Add-ons" tab
4. Click "Install..." and select the downloaded .py file
5. Enable the addon by checking the box next to "Object: Stylized Hair and Stubble"

## Usage

### Basic Workflow

1. Select a mesh object or choose one from the dropdown
2. Adjust hair and stubble settings as desired
3. Click "Create Hair", "Create Stubble", or "Create Both"
4. Fine-tune the appearance with the live controls
5. When satisfied, use GBH addon to convert to hair curves if needed

### Available Controls

**Hair Settings:**
- Density - Control how many hair strands
- Length - Adjust the hair length
- Thickness - Change hair strand thickness
- Color - Select hair color with standard Blender picker
- Grey % - Control the amount of grey (salt & pepper)

**Stubble Settings:**
- Density - Control stubble density
- Length - Adjust stubble length
- Thickness - Change stubble thickness
- Color - Select stubble color independently
- Grey % - Control grey percentage for stubble separately

**Transparency:**
- Fully Transparent - Make the mesh invisible, showing only hair
- Scalp Opacity - Fine-tune partial transparency

## Troubleshooting

**Hair Not Attached to Mesh:**
If hair appears floating or disconnected:
1. Go to Particle Edit mode (select object > Particle Edit in dropdown)
2. Then return to Object mode
3. Try clicking "Create Hair/Stubble" again

**Performance Issues:**
If experiencing slowdown during animation:
1. Reduce the density values
2. Lower the number of children particles
3. Keep viewport display settings low while working

## Credits

Created by Kindjhali
License: MIT


## Compatibility

- ✅ Blender 4.0+
- ✅ Blender 4.4
- ✅ Works with GBH addon
- ✅ Works with Cycles and Eevee

## To-Do / Future Updates

- Add presets for common hair styles
- Support for longer hair types
- Improved strand shaping controls
- Export/import settings
