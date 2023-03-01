# Script to take the skeleton out of a GLTF model taken from Kuro no Kiseki, and use
# that to create a VG map for an entire model.  Uses functions from make_vgmap_from_gltf.py.
#
# Requires Julian Uy's parser to generate the GLTF model.  Huge thank you to Julian Uy.
# ED9 MDL Parser: https://gist.github.com/uyjulian/9a9d6395682dac55d113b503b1172009
#
# GitHub eArmada8/misc_kiseki

from make_vgmap_from_gltf import *
import json

if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    model = pick_gltf('*COMPLETE MODEL*')
    model_data = obtain_model_data(model['gltf_filename'])
    model_nodes = model_data['nodes']
    model_skin = [x['skin'] for x in model_data['nodes']\
        if 'skin' in x.keys() and 'mesh' in x.keys() and x['mesh'] == model['gltf_mesh_id']][0]
    model_bones = model_data["skins"][model_skin]["joints"]
    model_bone_nodes = [model_nodes[i] for i in model_bones]
    model_bones = create_bone_dictionary(model_bone_nodes)
    vgmap = {}
    for i in range(len(model_bones)):
        vgmap[model_bones[i]['name']] = model_bones[i]['num']
    overwrite = False
    output_file = model['gltf_filename'][:-5]+'_' + model_data["meshes"][model['gltf_mesh_id']]["name"] +'.vgmap'
    if os.path.exists(output_file):
        if str(input(output_file + " exists! Overwrite? (y/N) ")).lower()[0:1] == 'y':
            overwrite = True
    if (overwrite == True) or not os.path.exists(output_file):
        with open(output_file, "wb") as f:
            f.write(json.dumps(vgmap, indent=5).encode("utf-8"))
    meshes = retrieve_meshes()
    for i in range(len(meshes)):
        overwrite = False
        vgmap_name = meshes[i] + '.vgmap'
        if os.path.exists(vgmap_name):
            if str(input(vgmap_name + " exists! Overwrite? (y/N) ")).lower()[0:1] == 'y':
                overwrite = True
        if (overwrite == True) or not os.path.exists(vgmap_name):
            with open(vgmap_name, 'wb') as f:
                f.write(json.dumps(vgmap, indent=5).encode("utf-8"))
