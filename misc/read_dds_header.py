# Short script to decipher DDS headers
# Use the following guide to decipher the output:
# https://learn.microsoft.com/en-us/windows/win32/direct3ddds/dx-graphics-dds-pguide
#
# GitHub eArmada8/misc_kiseki

import sys, os, glob, struct, json

dxgi_formats = {\
    "0": "DXGI_FORMAT_UNKNOWN",\
    "1": "DXGI_FORMAT_R32G32B32A32_TYPELESS",\
    "2": "DXGI_FORMAT_R32G32B32A32_FLOAT",\
    "3": "DXGI_FORMAT_R32G32B32A32_UINT",\
    "4": "DXGI_FORMAT_R32G32B32A32_SINT",\
    "5": "DXGI_FORMAT_R32G32B32_TYPELESS",\
    "6": "DXGI_FORMAT_R32G32B32_FLOAT",\
    "7": "DXGI_FORMAT_R32G32B32_UINT",\
    "8": "DXGI_FORMAT_R32G32B32_SINT",\
    "9": "DXGI_FORMAT_R16G16B16A16_TYPELESS",\
    "10": "DXGI_FORMAT_R16G16B16A16_FLOAT",\
    "11": "DXGI_FORMAT_R16G16B16A16_UNORM",\
    "12": "DXGI_FORMAT_R16G16B16A16_UINT",\
    "13": "DXGI_FORMAT_R16G16B16A16_SNORM",\
    "14": "DXGI_FORMAT_R16G16B16A16_SINT",\
    "15": "DXGI_FORMAT_R32G32_TYPELESS",\
    "16": "DXGI_FORMAT_R32G32_FLOAT",\
    "17": "DXGI_FORMAT_R32G32_UINT",\
    "18": "DXGI_FORMAT_R32G32_SINT",\
    "19": "DXGI_FORMAT_R32G8X24_TYPELESS",\
    "20": "DXGI_FORMAT_D32_FLOAT_S8X24_UINT",\
    "21": "DXGI_FORMAT_R32_FLOAT_X8X24_TYPELESS",\
    "22": "DXGI_FORMAT_X32_TYPELESS_G8X24_UINT",\
    "23": "DXGI_FORMAT_R10G10B10A2_TYPELESS",\
    "24": "DXGI_FORMAT_R10G10B10A2_UNORM",\
    "25": "DXGI_FORMAT_R10G10B10A2_UINT",\
    "26": "DXGI_FORMAT_R11G11B10_FLOAT",\
    "27": "DXGI_FORMAT_R8G8B8A8_TYPELESS",\
    "28": "DXGI_FORMAT_R8G8B8A8_UNORM",\
    "29": "DXGI_FORMAT_R8G8B8A8_UNORM_SRGB",\
    "30": "DXGI_FORMAT_R8G8B8A8_UINT",\
    "31": "DXGI_FORMAT_R8G8B8A8_SNORM",\
    "32": "DXGI_FORMAT_R8G8B8A8_SINT",\
    "33": "DXGI_FORMAT_R16G16_TYPELESS",\
    "34": "DXGI_FORMAT_R16G16_FLOAT",\
    "35": "DXGI_FORMAT_R16G16_UNORM",\
    "36": "DXGI_FORMAT_R16G16_UINT",\
    "37": "DXGI_FORMAT_R16G16_SNORM",\
    "38": "DXGI_FORMAT_R16G16_SINT",\
    "39": "DXGI_FORMAT_R32_TYPELESS",\
    "40": "DXGI_FORMAT_D32_FLOAT",\
    "41": "DXGI_FORMAT_R32_FLOAT",\
    "42": "DXGI_FORMAT_R32_UINT",\
    "43": "DXGI_FORMAT_R32_SINT",\
    "44": "DXGI_FORMAT_R24G8_TYPELESS",\
    "45": "DXGI_FORMAT_D24_UNORM_S8_UINT",\
    "46": "DXGI_FORMAT_R24_UNORM_X8_TYPELESS",\
    "47": "DXGI_FORMAT_X24_TYPELESS_G8_UINT",\
    "48": "DXGI_FORMAT_R8G8_TYPELESS",\
    "49": "DXGI_FORMAT_R8G8_UNORM",\
    "50": "DXGI_FORMAT_R8G8_UINT",\
    "51": "DXGI_FORMAT_R8G8_SNORM",\
    "52": "DXGI_FORMAT_R8G8_SINT",\
    "53": "DXGI_FORMAT_R16_TYPELESS",\
    "54": "DXGI_FORMAT_R16_FLOAT",\
    "55": "DXGI_FORMAT_D16_UNORM",\
    "56": "DXGI_FORMAT_R16_UNORM",\
    "57": "DXGI_FORMAT_R16_UINT",\
    "58": "DXGI_FORMAT_R16_SNORM",\
    "59": "DXGI_FORMAT_R16_SINT",\
    "60": "DXGI_FORMAT_R8_TYPELESS",\
    "61": "DXGI_FORMAT_R8_UNORM",\
    "62": "DXGI_FORMAT_R8_UINT",\
    "63": "DXGI_FORMAT_R8_SNORM",\
    "64": "DXGI_FORMAT_R8_SINT",\
    "65": "DXGI_FORMAT_A8_UNORM",\
    "66": "DXGI_FORMAT_R1_UNORM",\
    "67": "DXGI_FORMAT_R9G9B9E5_SHAREDEXP",\
    "68": "DXGI_FORMAT_R8G8_B8G8_UNORM",\
    "69": "DXGI_FORMAT_G8R8_G8B8_UNORM",\
    "70": "DXGI_FORMAT_BC1_TYPELESS",\
    "71": "DXGI_FORMAT_BC1_UNORM",\
    "72": "DXGI_FORMAT_BC1_UNORM_SRGB",\
    "73": "DXGI_FORMAT_BC2_TYPELESS",\
    "74": "DXGI_FORMAT_BC2_UNORM",\
    "75": "DXGI_FORMAT_BC2_UNORM_SRGB",\
    "76": "DXGI_FORMAT_BC3_TYPELESS",\
    "77": "DXGI_FORMAT_BC3_UNORM",\
    "78": "DXGI_FORMAT_BC3_UNORM_SRGB",\
    "79": "DXGI_FORMAT_BC4_TYPELESS",\
    "80": "DXGI_FORMAT_BC4_UNORM",\
    "81": "DXGI_FORMAT_BC4_SNORM",\
    "82": "DXGI_FORMAT_BC5_TYPELESS",\
    "83": "DXGI_FORMAT_BC5_UNORM",\
    "84": "DXGI_FORMAT_BC5_SNORM",\
    "85": "DXGI_FORMAT_B5G6R5_UNORM",\
    "86": "DXGI_FORMAT_B5G5R5A1_UNORM",\
    "87": "DXGI_FORMAT_B8G8R8A8_UNORM",\
    "88": "DXGI_FORMAT_B8G8R8X8_UNORM",\
    "89": "DXGI_FORMAT_R10G10B10_XR_BIAS_A2_UNORM",\
    "90": "DXGI_FORMAT_B8G8R8A8_TYPELESS",\
    "91": "DXGI_FORMAT_B8G8R8A8_UNORM_SRGB",\
    "92": "DXGI_FORMAT_B8G8R8X8_TYPELESS",\
    "93": "DXGI_FORMAT_B8G8R8X8_UNORM_SRGB",\
    "94": "DXGI_FORMAT_BC6H_TYPELESS",\
    "95": "DXGI_FORMAT_BC6H_UF16",\
    "96": "DXGI_FORMAT_BC6H_SF16",\
    "97": "DXGI_FORMAT_BC7_TYPELESS",\
    "98": "DXGI_FORMAT_BC7_UNORM",\
    "99": "DXGI_FORMAT_BC7_UNORM_SRGB",\
    "100": "DXGI_FORMAT_AYUV",\
    "101": "DXGI_FORMAT_Y410",\
    "102": "DXGI_FORMAT_Y416",\
    "103": "DXGI_FORMAT_NV12",\
    "104": "DXGI_FORMAT_P010",\
    "105": "DXGI_FORMAT_P016",\
    "106": "DXGI_FORMAT_420_OPAQUE",\
    "107": "DXGI_FORMAT_YUY2",\
    "108": "DXGI_FORMAT_Y210",\
    "109": "DXGI_FORMAT_Y216",\
    "110": "DXGI_FORMAT_NV11",\
    "111": "DXGI_FORMAT_AI44",\
    "112": "DXGI_FORMAT_IA44",\
    "113": "DXGI_FORMAT_P8",\
    "114": "DXGI_FORMAT_A8P8",\
    "115": "DXGI_FORMAT_B4G4R4A4_UNORM",\
    "130": "DXGI_FORMAT_P208",\
    "131": "DXGI_FORMAT_V208",\
    "132": "DXGI_FORMAT_V408"\
}
D3D10_res_dim_enum = ["D3D10_RESOURCE_DIMENSION_UNKNOWN", "D3D10_RESOURCE_DIMENSION_BUFFER",\
    "D3D10_RESOURCE_DIMENSION_TEXTURE1D", "D3D10_RESOURCE_DIMENSION_TEXTURE2D",\
    "D3D10_RESOURCE_DIMENSION_TEXTURE3D"]

def read_dds_header(filename):
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            magic = f.read(4).decode("ASCII")
            if magic == 'DDS ':
                header = {}
                header['dwSize'], header['dwFlags'], header['dwHeight'], header['dwWidth'],\
                    header['dwPitchOrLinearSize'], header['dwDepth'], header['dwMipMapCount']\
                    = struct.unpack("<7I", f.read(28))
                f.seek(44,1) # Skipping 'dwReserved1'
                pixel_format = {}
                pixel_format['dwSize'], pixel_format['dwFlags'] = struct.unpack("<2I", f.read(8))
                pixel_format['dwFourCC'] = f.read(4).decode("ASCII")
                pixel_format['dwRGBBitCount'], pixel_format['dwRBitMask'], pixel_format['dwGBitMask'],\
                    pixel_format['dwBBitMask'], pixel_format['dwABitMask'] = struct.unpack("<5I", f.read(20))
                header['pixel_format'] = pixel_format
                header['dwCaps'], header['dwCaps2'], header['dwCaps3'], header['dwCaps4'] = struct.unpack("<4I", f.read(16))
                f.seek(4,1) # Skipping 'dwReserved2'
                if header['pixel_format']['dwFourCC'] == 'DX10':
                    dxt10_header = {}
                    dxt10_header['dxgiFormat'] = dxgi_formats[str(struct.unpack("<I", f.read(4))[0])]
                    dxt10_header['resourceDimension'] = D3D10_res_dim_enum[struct.unpack("<I", f.read(4))[0]]
                    dxt10_header['miscFlag'], dxt10_header['arraySize'], dxt10_header['miscFlags2']\
                         = struct.unpack("<3I", f.read(12))
                    header['dxt10_header'] = dxt10_header
                return(header)
            else:
                return(False)
    else:
        return(False)

def process_dds (dds_file, overwrite = False):
    dds_header_info = read_dds_header(dds_file)
    dds_header_json_filename = dds_file[:-4] + '_dds_header_info.json'
    if dds_header_info != False:
        if os.path.exists(dds_header_json_filename) and (overwrite == False):
            if str(input(dds_header_json_filename + " exists! Overwrite? (y/N) ")).lower()[0:1] == 'y':
                overwrite = True
        if (overwrite == True) or not os.path.exists(dds_header_json_filename):
            with open(dds_header_json_filename, 'wb') as f:
                f.write(json.dumps(dds_header_info, indent=4).encode("utf-8"))

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    # If argument given, attempt to export from file in argument
    if len(sys.argv) > 1:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('-o', '--overwrite', help="Overwrite existing files", action="store_true")
        parser.add_argument('dds_filename', help="Name of dds file to parse header (required).")
        args = parser.parse_args()
        if os.path.exists(args.dds_filename) and args.dds_filename[-4:].lower() == '.dds':
            process_dds(args.dds_filename, overwrite = args.overwrite)
    else:
        dds_files = glob.glob('*.dds')
        for i in range(len(dds_files)):
            process_dds(dds_files[i])
