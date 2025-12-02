# Tool to decompress Hajimari no Kiseki assets from the CLE release
# Usage:  Run by itself without commandline arguments and it will decompress all files in the folder.
# For command line options, run:
# /path/to/python3 cle_haji_decrypt_decompress.py --help
#
# Requires blowfish for CLE assets.
# These can be installed by:
# /path/to/python3 -m pip install blowfish
#
# GitHub eArmada8/misc_kiseki

# Thank you to authors of Kuro Tools for the original decrypt function and to wheat32 for the key
# https://github.com/nnguyen259/KuroTools
# https://github.com/wheat32/HajimariQuickTranslation

import blowfish, struct, shutil, sys, os, glob

key = b'ed8psv5_steam'
cipher = blowfish.Cipher(key)
to_decrypt = 0x40104241

def processCLE (f):
    f.seek(0)
    magic, size = struct.unpack('<2I', f.read(8))
    if (magic == to_decrypt):
        unc_data = bytearray()
        unc_data.extend(b"".join(cipher.decrypt_ecb(f.read((size//8)*8))))
        unc_data.extend(f.read())
        return(unc_data)
    else:
        return False

def processFile(cle_asset_filename):
    with open(cle_asset_filename, 'rb') as f:
        processed_data = processCLE(f)
        if processed_data != False:
            # Make a backup
            shutil.copy2(cle_asset_filename, cle_asset_filename + '.original_encrypted')
            with open(cle_asset_filename, 'wb') as f:
                f.write(processed_data)
    return

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    # If argument given, attempt to export from file in argument
    if len(sys.argv) > 1:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('cle_asset_filename', help="Name of file to decrypt / decompress (required).")
        args = parser.parse_args()
        if os.path.exists(args.cle_asset_filename):
            processFile(args.cle_asset_filename)
    else:
        all_files = [x for x in glob.glob('*.*', recursive = False)\
            if x not in glob.glob('*.original_encrypted', recursive = False)]
        for i in range(len(all_files)):
            processFile(all_files[i])