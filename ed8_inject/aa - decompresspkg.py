# Short script to remove compression from Hajimari no Kiseki packagers.  
# Output goes into the decompressed_output folder.
# GitHub eArmada8/misc_kiseki

import sys, os, shutil, struct
from unpackpkg import * # compression libraries

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    # Grab the name of the package to decompress
    try:
        sourcefile = sys.argv[1].lower()
        if sourcefile[-4:] == '.pkg':
            sourcefile = sourcefile[:-4] # Strip off the '.pkg' if present
        if not os.path.exists(sourcefile + '.pkg'):
            raise Exception('Error: Package "' + sourcefile + '" does not exist!')
    except IndexError:
        sourcefile = str(input("Please enter the name (e.g. C_CHR000_C02) of package: "))
        if sourcefile[-4:] == '.pkg':
            sourcefile = sourcefile[:-4] # Strip off the '.pkg' if present
        while not os.path.exists(sourcefile + '.pkg'):
            sourcefile = str(input("File does not exist.  Please enter the name (e.g. C_CHR000_C02) of package: "))
            if sourcefile[-4:] == '.pkg':
                sourcefile = sourcefile[:-4] # Strip off the '.pkg' if present
    sourcefile = sourcefile.upper()

    # Let's make an output directory, because otherwise we would have to delete / overwrite files
    if not os.path.exists('decompressed_output'): 
        os.mkdir('decompressed_output')

    # Read source model into memory
    with open(sourcefile + '.pkg', 'rb') as f:
        source_file_data = bytearray(f.read())
        f.seek(4)
        package_file_entries = []
        total_file_entries, = struct.unpack("<I", f.read(4))

        for i in range(total_file_entries):
            file_entry_name, file_entry_uncompressed_size, file_entry_compressed_size, file_entry_offset, file_entry_flags = struct.unpack("<64sIIII", f.read(64+4+4+4+4))
            package_file_entries.append([file_entry_offset, file_entry_compressed_size, file_entry_uncompressed_size, file_entry_flags])

        # Grab the original header as a byte array, we will patch this directly later (not elegant I know)
        patched_header = source_file_data[0:package_file_entries[0][0]]
        archive_start_offset = package_file_entries[0][0]
        
        # Generate the files, to be combined with the patched header
        package_archive = bytes()
        new_header_data = []

        current_offset = archive_start_offset
        for file_entry_number in range(len(package_file_entries)):
            file_entry = package_file_entries[file_entry_number]
            f.seek(file_entry[0])
            output_data = None
            if file_entry[3] & 2:
                # This is the crc32 of the file, but we don't handle this yet
                f.seek(4, io.SEEK_CUR)
            if file_entry[3] & 4:
                output_data = uncompress_lz4(f, file_entry[2], file_entry[1])
            elif file_entry[3] & 8:
                if "zstandard" in sys.modules:
                    output_data = uncompress_zstd(f, file_entry[2], file_entry[1])
                else:
                    raise Exception("File could not be decompressed because zstandard module is not installed")
            elif file_entry[3] & 1:
                output_data = uncompress_nislzss(f, file_entry[2], file_entry[1])
            else:
                output_data = f.read(file_entry[2])
            if output_data is not None:
                new_header_data.append([current_offset, len(output_data), len(output_data), 0])
                package_archive = package_archive + output_data
                current_offset = current_offset + len(output_data)

    # Set the new file offsets into the patched file data
    for offset in range(len(new_header_data)):
        offset_location = (offset+1)*80-8
        patched_header[offset_location:offset_location+16] = new_header_data[offset][1].to_bytes(4, 'little') + new_header_data[offset][2].to_bytes(4, 'little') + new_header_data[offset][0].to_bytes(4, 'little') + new_header_data[offset][3].to_bytes(4, 'little')

    #Reassemble the .pkg file
    patched_file_data = patched_header + package_archive

    # Write patched model into target
    with open('decompressed_output/' + sourcefile + '.pkg', 'wb') as f:
        f.write(patched_file_data)

