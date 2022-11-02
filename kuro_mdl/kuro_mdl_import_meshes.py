# Research tool to understand ED9 / Kuro no Kiseki models in mdl format.  Replace mesh section of
# Kuro no Kiseki mdl file with individual buffers previously exported.  Based on Uyjulian's script.
# Usage:  Run by itself without commandline arguments and it will read only the mesh section of
# every model it finds in the folder and replace them with fmt / ib / vb files in the same named
# directory.
#
# For command line options (including option to dump vertices), run:
# /path/to/python3 kuro_mdl_export_meshes.py
#
# Requires both blowfish and zstandard for CLE assets.
# These can be installed by:
# /path/to/python3 -m pip install blowfish zstandard
#
# GitHub eArmada8/misc_kiseki

import io, struct, sys, os, glob, json, blowfish, operator, zstandard
from itertools import chain
from lib_fmtibvb import *
from kuro_mdl_export_meshes import *

def make_pascal_string(string):
    return struct.pack("<B", len(string)) + string.encode("utf8")

def insert_mesh_data (mdl_data, mesh_section_data):
    with io.BytesIO(mdl_data) as f:
        new_mdl_data = f.read(12) #Header
        while True:
            current_offset = f.tell()
            section = f.read(8)
            section_info = {}
            try:
                section_info["type"], section_info["size"] = struct.unpack("<II",section)
                section += f.read(section_info["size"])
            except:
                break
            if section_info["type"] == 1: # Mesh section to replace
                section = mesh_section_data
            new_mdl_data += section
        # Catch the null bytes at the end of the stream
        f.seek(current_offset,0)
        new_mdl_data += f.read()
        return(new_mdl_data)

def build_mesh_section (mdl_filename):
    mesh_struct = read_struct_from_json(mdl_filename + "/mdl_info.json")
    output_buffer = struct.pack("<I", len(mesh_struct))
    for i in range(len(mesh_struct)):
        mesh_block = struct.pack("<I", len(mesh_struct[i]["primitives"]))
        for j in range(len(mesh_struct[i]["primitives"])):
            mesh_filename = mdl_filename + '/{0}_{1}_{2:02d}'.format(i, mesh_struct[i]["name"], j)
            fmt = read_fmt(mesh_filename + '.fmt')
            ib = list(chain.from_iterable(read_ib(mesh_filename + '.ib', fmt)))
            vb = read_vb(mesh_filename + '.vb', fmt)
            primitive_buffer = struct.pack("<2I", mesh_struct[i]["primitives"][j]["material_offset"], len(vb)+1)
            for k in range(len(vb)):
                match vb[k]["SemanticName"]:
                    case "POSITION":
                        type_int = 0
                    case "NORMAL":
                        type_int = 1
                    case "TANGENT":
                        type_int = 2
                    case "UNKNOWN":
                        type_int = 3
                    case "TEXCOORD":
                        type_int = 4
                    case "BLENDWEIGHTS":
                        type_int = 5
                    case "BLENDINDICES":
                        type_int = 6
                dxgi_format = fmt["elements"][k]["Format"].split('DXGI_FORMAT_')[-1]
                dxgi_format_split = dxgi_format.split('_')
                vec_format = re.findall("[0-9]+",dxgi_format_split[0])
                vec_elements = len(vec_format)
                vec_stride = int(int(vec_format[0]) * len(vec_format) / 8)
                match dxgi_format_split[1]:
                    case "FLOAT":
                        element_type = 'f'
                    case "UINT":
                        element_type = 'I' # Assuming 32-bit since Kuro models all use 32-bit
                raw_buffer = struct.pack("<{0}{1}".format(vec_elements*len(vb[k]["Buffer"]), element_type), *list(chain.from_iterable(vb[k]["Buffer"])))
                primitive_buffer += struct.pack("<3I", type_int, len(raw_buffer), vec_stride) + raw_buffer
            # After VB, need to add IB
            # Making assumptions here that it will always be in Rxx_UINT format, saves a bunch of code
            vec_stride = int(int(re.findall("[0-9]+",fmt["format"].split('DXGI_FORMAT_')[-1].split('_')[0])[0]) / 8)
            raw_ibuffer = struct.pack("<{0}I".format(len(ib), element_type), *ib)
            primitive_buffer += struct.pack("<3I", 7, len(raw_ibuffer), vec_stride) + raw_ibuffer
            mesh_block += primitive_buffer
        node_block = struct.pack("<I", len(mesh_struct[i]["nodes"]))
        if len(mesh_struct[i]["nodes"]) > 0:
            for j in range(len(mesh_struct[i]["nodes"])):
                node_block += make_pascal_string(mesh_struct[i]["nodes"][j]["name"])
                node_block += struct.pack("<16f", *list(chain.from_iterable(mesh_struct[i]["nodes"][j]["matrix"])))
        mesh_block += node_block
        raw_section2 = struct.pack("<3fI3f4I", *mesh_struct[i]["section2"]["data"])
        section2_block = struct.pack("<I", len(raw_section2)) + raw_section2
        mesh_block = make_pascal_string(mesh_struct[i]["name"]) + struct.pack("<I", len(mesh_block)) + mesh_block + section2_block
        output_buffer += mesh_block
    return(struct.pack("<2I", 1, len(output_buffer)) + output_buffer)

def process_mdl (mdl_file, overwrite = False):
    with open(mdl_file, "rb") as f:
        mdl_data = f.read()
    mdl_data = decryptCLE(mdl_data)
    mesh_data = build_mesh_section(mdl_file[:-4])
    new_mdl_data = insert_mesh_data(mdl_data, mesh_data)
    if os.path.exists(mdl_file[:-4] + '_modified.mdl') and (overwrite == False):
        if str(input(mdl_file[:-4] + "_modified.mdl already exists, please confirm overwrite: (y/N) ")).lower()[0:1] == 'y':
            overwrite = True
    if (overwrite == True) or not os.path.exists(mdl_file[:-4] + '_modified.mdl'):
        with open(mdl_file[:-4] + '_modified.mdl','wb') as f:
            f.write(new_mdl_data)

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    # If argument given, attempt to import into file in argument
    if len(sys.argv) > 1:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('-o', '--overwrite', help="Overwrite existing files", action="store_true")
        parser.add_argument('mdl_filename', help="Name of mdl file to import into (required).")
        args = parser.parse_args()
        if os.path.exists(args.mdl_filename) and args.mdl_filename[-4:].lower() == '.mdl':
            process_mdl(args.mdl_filename, overwrite = args.overwrite)
    else:
        mdl_files = glob.glob('*.mdl')
        mdl_files = [x for x in mdl_files if os.path.isdir(x[:-4])]
        for i in range(len(mdl_files)):
            process_mdl(mdl_files[i])