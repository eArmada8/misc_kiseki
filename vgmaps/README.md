# VGMap Toolset for Kuro no Kiseki
A set of scripts used for easy mapping of vertex groups.  When obtaining meshes from a 3DMigoto frame dump, the vertex groups in the frame dump are already numbered for the skeleton, but those mappings are lost when importing into Blender unless a .vgmap file is there to bind the number to a name.  This uses the amazing ED9 MDL parser from uyjulian (github.com/uyjulian) to obtain the names of the bones and generate .vgmap files to simplify mesh rigging and mesh transfer.

## Credits:
99.9% of my understanding of the MDL format comes from the reverse engineering work of Julian Uy (github.com/uyjulian), and specifically his MDL to GLTF convertor: https://gist.github.com/uyjulian/9a9d6395682dac55d113b503b1172009

The code to decrypt and decompress CLE assets comes from KuroTools (https://github.com/nnguyen259/KuroTools), and I also looked through MDL convertor in KuroTools by TwnKey (github.com/TwnKey) to understand the MDL format.

None of this would be possible without the work of DarkStarSword and his amazing 3DMigoto-Blender plugin, of course.

I am very thankful for uyjulian, TwnKey, DarkStarSword, the KuroTools team and the Kiseki modding discord for their brilliant work and for sharing that work so freely.

## Requirements:
1. Python 3 and newer is required for use of these scripts.  It is free from the Microsoft Store, for Windows users.  For Linux users, please consult your distro.
2. The blowfish and zstandard modules for python are needed.  Install by typing "python3 -m pip install blowfish zstandard" in the command line / shell.  (The io, re struct, sys, os, glob, ctypes, array, pprint, math, json, operator, and argparse modules are also required, but these are all already included in most basic python installations.)
3. The output can be imported into Blender using DarkStarSword's amazing plugin: https://github.com/DarkStarSword/3d-fixes/blob/master/blender_3dmigoto.py
4. make_complete_vgmap.py is dependent on make_vgmap_from_gltf.py, which must be in the same folder.

## Usage:
### kuro_mdl_to_gltf.py
This script is a fork of https://gist.github.com/uyjulian/9a9d6395682dac55d113b503b1172009 by uyjulian.  It converts Kuro 1 MDL files to glTF.  My fork incorporates automatic decryption / decompression of CLE assets, and also does not require command-line usage.  When double-clicked, it will search for and convert all the MDL files in the current folder.  Decryption algorithm comes from KuroTools.  All the remaining tools rely on the glTF output of this script.  (This does not work for Kuro 2, please use Kuro MDL Tools.)

### make_vgmap_from_gltf.py
This script will load the skeleton from the glTF model provided, then it will load each mesh and generate a .vgmap file with proper bone names.  Place in the same folder as the glTF and the meshes in .fmt/.ib/.vb format (only the .fmt and .vb files are used), and double-click the script.  For each mesh, it will ask you which skeleton you would like to use (the mdl file generally includes 3 - hair, body and shadow).  It only includes non-empty groups in the final .vgmap - if you would like the entire skeleton, use make_complete_vgmap.py.

### make_complete_vgmap.py
This script does the same thing as make_vgmap_from_gltf.py, except it will include all vertex groups from the skeleton you select, rather than just non-empty groups.  This is primarily useful when preparing a mesh to be a recipient of a mesh join.

### compare_vgmaps.py
This script will take two .vgmap files, and create two lists of missing groups (groups in the first .vgmap that are not in the second .vgmap, and vice versa) as JSON files.  To be used with lock_common_groups.py.

### blender_lock_groups_with_vgmap.py
*This is a Blender add-on.*  This addon will ask for one or more .vgmap files, and will then either lock or unlock groups based on whether they are in the .vgmap file(s).  Groups that are present in the skeleton you wish to port to will be locked, and groups that are absent will be unlocked.  The add-on is located at Object Data Properties > Vertex Groups > Vertex Group Specials.

### blender_delete_empty_vertex_groups.py
*This is a Blender add-on.*  This addon will delete any vertex groups that do not have any vertices in them.  If you have deleted part of a mesh, you can run this add-on to delete any vertex groups that are now empty.  The add-on is located at Object Data Properties > Vertex Groups > Vertex Group Specials.
