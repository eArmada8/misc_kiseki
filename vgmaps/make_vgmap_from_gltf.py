# Script to take the skeleton out of a GLTF model taken from Kuro no Kiseki, and use
# that to create a VG map for a mesh dumped using 3DMigoto (to ease re-import and mesh
# transfer).
#
# Requires Julian Uy's parser to generate the GLTF model.  Huge thank you to Julian Uy.
# ED9 MDL Parser: https://gist.github.com/uyjulian/9a9d6395682dac55d113b503b1172009
#
# GitHub eArmada8/misc_kiseki

import json, sys, os, struct, glob, re, ctypes

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
    #Determine the offsets used in the combined buffer by parsing the FMT file
    semantics = []
    formats = []
    offsets = []
    with open(meshname + '.fmt', 'r') as f:
        for line in f:
            if line[0:6] == 'stride':
                combined_stride = int(line[8:-1])
            if line[2:14] == 'SemanticName':
                semantics.append(line[16:-1])
            if line[2:8] == 'Format':
                formats.append(line[10:-1])
            if line[2:19] == 'AlignedByteOffset':
                offsets.append(int(line[21:-1]))

    #Determine the strides to be used in the individual buffers
    strides = []
    for i in range(len(offsets)):
        if i == len(offsets) - 1:
            strides.append(combined_stride - offsets[i])
        else:
            strides.append(offsets[i+1] - offsets[i])

    #Figure out where the indices are.
    buffer_element_offset = offsets[semantics.index('BLENDINDICES')]
    buffer_element_stride = strides[semantics.index('BLENDINDICES')]

    #Figure out the weight group format (Thank you to DarkStarSword for regex pattern)
    if re.match(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]8)+_UINT''',formats[semantics.index('BLENDINDICES')]):
        buffer_element_format = 'uint8'
    elif re.match(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]16)+_UINT''',formats[semantics.index('BLENDINDICES')]):
        buffer_element_format = 'uint16'
    elif re.match(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]32)+_UINT''',formats[semantics.index('BLENDINDICES')]):
        buffer_element_format = 'uint32'
    else:
        return(False)

    #Grab the blend indices from the vertex buffer
    with open(meshname + '.vb', 'rb') as f:
        #Count the total number of vertices
        vertex_count = int(len(f.read())/combined_stride)
        indices = []
        for i in range(vertex_count):
            f.seek(combined_stride * i + buffer_element_offset, 0)
            if buffer_element_format == 'uint8':
                for j in range(int(buffer_element_stride)):
                    rawindex, = struct.unpack('<I', f.read(1)+b'\x00\x00\x00')
                    index = ctypes.c_uint8(int.from_bytes(f.read(1), byteorder="little")).value
                    indices.append(index)
            if buffer_element_format == 'uint16':
                for j in range(int(buffer_element_stride / 2)):
                    rawindex, = struct.unpack('<I', f.read(2)+b'\x00\x00')
                    index = ctypes.c_uint16(rawindex).value
                    indices.append(index)
            if buffer_element_format == 'uint32':
                for j in range(int(buffer_element_stride / 4)):
                    rawindex, = struct.unpack('<I', f.read(4))
                    index = ctypes.c_uint32(rawindex).value
                    indices.append(index)

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
    model_bones = model_data["skins"][model['gltf_mesh_id']]["joints"]
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
