# Script to take the skeleton out of a GLTF model taken from Kuro no Kiseki, and use
# that to create a VG map for a mesh dumped using 3DMigoto (to ease re-import and mesh
# transfer).
#
# Requires Julian Uy's parser to generate the GLTF model.  Huge thank you to Julian Uy.
# ED9 MDL Parser: https://gist.github.com/uyjulian/9a9d6395682dac55d113b503b1172009
#
# GitHub eArmada8/misc_kiseki

import json, sys, os, struct, glob
from lib_fmtibvb import *

# Read and parse gltf into python dictionary
def obtain_model_data(gltf_filename):
    with open(gltf_filename, 'r') as f:
        model_data = json.loads(f.read())
        # model_data.pop("buffers")
    return(model_data)

# Take the nodes from the dictionary and create a list of bones and their indices
def create_bone_dictionary(model_nodes):
    bone_dictionary = []
    bone_num = 0 # 3DMigoto numbering excludes non-bone nodes, apparently?
    for i in range(len(model_nodes)):
        bone = {}
        bone['num'] = bone_num
        bone['name'] = model_nodes[i]['name']
        bone_dictionary.append(bone)
        bone_num += 1
    return(bone_dictionary)

def read_text_vertex_buffer(vb_filename):
    bone_list = []
    with open(vb_filename, 'r') as f:
        for line in f:
            line_list = line.strip().split('BLENDINDICES: ')
            if len(line_list) > 1: # If positive, line contains BLENDINDICES
                bone_list.extend(line_list[1].split(', '))
    bone_list = list(set(bone_list))
    for i in range(len(bone_list)):
        bone_list[i] = int(bone_list[i])
    bone_list.sort()
    return(bone_list)

def read_raw_vertex_buffer(meshname):
    fmt = read_fmt(meshname + '.fmt')
    #Figure out where the indices are.
    blendindices_element = [i for i in range(len(fmt['elements'])) if fmt['elements'][i]['SemanticName'] == 'BLENDINDICES'][0]

    #Grab the blend indices from the vertex buffer
    vb = read_vb(meshname + '.vb', fmt)
    indices = [x for y in vb[blendindices_element]['Buffer'] for x in y]

    #Sort and pull out unique bones
    bone_list = list(set(indices))
    for i in range(len(bone_list)):
        bone_list[i] = int(bone_list[i])
    bone_list.sort()
    return(bone_list)

def make_vgmap(list_of_bones, bone_dictionary):
    vgmap_output = '{\n'
    for i in range(len(list_of_bones)):
        vgmap_output += '\t"' + bone_dictionary[list_of_bones[i]]['name'] + '": ' \
            + str(bone_dictionary[list_of_bones[i]]['num'])
        if i < range(len(list_of_bones))[-1]:
            vgmap_output += ','
        vgmap_output += '\n'
    vgmap_output += '}\n'
    return(vgmap_output)

def pick_gltf_mesh_for_skeleton(gltf_filename, meshname):
    model_data = obtain_model_data(gltf_filename)
    if model_data.get("meshes",False) == False:
        print("Error: GLTF file missing meshes!")
        return False
    elif len(model_data.get("meshes")) == 1:
        return(0) # Only one mesh to choose from
    else:
        print('For processing mesh ' + meshname + ', which mesh has your skeleton?\n')
        for i in range(len(model_data.get("meshes"))):
            print(str(i+1) + '. ' + model_data["meshes"][i]["name"])
        gltf_mesh_choice = -1
        while (gltf_mesh_choice < 0) or (gltf_mesh_choice >= len(model_data.get("meshes"))):
            try:
                gltf_mesh_choice = int(input("\nPlease enter which mesh to use:  ")) - 1 
            except ValueError:
                pass
        return(gltf_mesh_choice)

def pick_gltf(meshname):
    gltf_files = glob.glob('*gltf')
    gltf = {}
    if len(gltf_files) < 1:
        print("Error: A GLTF file is needed!")
        return False
    elif len(gltf_files) == 1:
        gltf['gltf_filename'] = (gltf_files[0]) # Only one model to choose from
    else:
        print('For processing mesh ' + meshname + ', which GLTF file has your skeleton?\n')
        for i in range(len(gltf_files)):
            print(str(i+1) + '. ' + gltf_files[i])
        gltf_file_choice = -1
        while (gltf_file_choice < 0) or (gltf_file_choice >= len(gltf_files)):
            try:
                gltf_file_choice = int(input("\nPlease enter which GLTF file to use:  ")) - 1 
            except ValueError:
                pass
        gltf['gltf_filename'] = gltf_files[gltf_file_choice]
    gltf['gltf_mesh_id'] = pick_gltf_mesh_for_skeleton(gltf['gltf_filename'], meshname)
    return(gltf)

def make_vgmap_for_bone_list(list_of_bones, meshname):
    model = pick_gltf(meshname)
    model_data = obtain_model_data(model['gltf_filename'])
    model_nodes = model_data['nodes']
    model_skin = [x['skin'] for x in model_data['nodes']\
        if 'skin' in x.keys() and 'mesh' in x.keys() and x['mesh'] == model['gltf_mesh_id']][0]
    model_bones = model_data["skins"][model_skin]["joints"]
    model_bone_nodes = [model_nodes[i] for i in model_bones]
    model_bones = create_bone_dictionary(model_bone_nodes)
    return(make_vgmap(list_of_bones, model_bones))

def retrieve_meshes():
    # Make a list of all mesh groups in the current folder, both fmt and vb files are necessary for processing
    fmts = [x[:-4] for x in glob.glob('*fmt')]
    vbs = [x[:-3] for x in glob.glob('*vb')]
    return [value for value in fmts if value in vbs]

if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    meshes = retrieve_meshes()
    for i in range(len(meshes)):
        overwrite = False
        bone_list = read_raw_vertex_buffer(meshes[i])
       
        vgmap = make_vgmap_for_bone_list(bone_list, meshes[i])
        vgmap_name = meshes[i] + '.vgmap'
        if os.path.exists(vgmap_name):
            if str(input(vgmap_name + " exists! Overwrite? (y/N) ")).lower()[0:1] == 'y':
                overwrite = True
        if (overwrite == True) or not os.path.exists(vgmap_name):
            with open(vgmap_name, 'w') as f:
                f.write(vgmap)
