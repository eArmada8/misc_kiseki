# Short script to inject one model in Tokyo Xanadu eX+ into another.  It always pulls the source file from the asset
# archive.  (Use the generic Kiseki injection script if you want to avoid this behavior!)
# GitHub eArmada8/misc_kiseki

import sys, os, shutil, struct, io
from txe_file_extract import * # TXe File Extraction Library
from unpackpkg import * # Needed due to XML compression

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    # Grab the name of the source model (model to inject)
    try:
        sourcefile = sys.argv[1].lower()
        if sourcefile[-4:] == '.pkg':
            sourcefile = sourcefile[:-4] # Strip off the '.pkg' if present
        if not (len(find_file(sourcefile + '.pkg', exact_match = True)) == 1):
            raise Exception('Error: Package "' + sourcefile + '" does not exist!')
    except IndexError:
        sourcefile = str(input("Please enter the name (e.g. C_PLY001_C02) of model to inject: "))
        if sourcefile[-4:] == '.pkg':
            sourcefile = sourcefile[:-4] # Strip off the '.pkg' if present
        while not (len(find_file(sourcefile + '.pkg', exact_match = True)) == 1):
            sourcefile = str(input("File does not exist.  Please enter the name (e.g. C_PLY001_C02) of model to inject: "))
            if sourcefile[-4:] == '.pkg':
                sourcefile = sourcefile[:-4] # Strip off the '.pkg' if present
    sourcefile = sourcefile.upper()

    # Grab the name of the target model (model to be replaced)
    try:
        targetfile = sys.argv[2].lower()
        if targetfile[-4:] == '.pkg':
            targetfile = targetfile[:-4] # Strip off the '.pkg' if present
        if not (len(find_file(targetfile + '.pkg', exact_match = True)) == 1):
            raise Exception('Error: Package "' + targetfile + '" does not exist!')
    except IndexError:
        targetfile = str(input("Please enter the name (e.g. C_PLY001_C02) of model to replace: "))
        if targetfile[-4:] == '.pkg':
            targetfile = targetfile[:-4] # Strip off the '.pkg' if present
        while not (len(find_file(targetfile + '.pkg', exact_match = True)) == 1):
            targetfile = str(input("File does not exist.  Please enter the name (e.g. C_PLY001_C02) of model to replace: "))
            if targetfile[-4:] == '.pkg':
                targetfile = targetfile[:-4] # Strip off the '.pkg' if present
    targetfile = targetfile.upper()

    # Generate the search and substitution strings to inject into the target model
    if sourcefile.split('_')[-1][0] == 'C':
        source_string = sourcefile
        target_string = targetfile
    else:
        source_string = sourcefile.split('_')[0] + '_' + sourcefile.split('_')[1]
        target_string = targetfile.split('_')[0] + '_' + targetfile.split('_')[1]
    offset_difference = len(target_string) - len(source_string)

    # Read source model into memory
    source_file_data = extract_filedata(find_file(sourcefile + '.pkg', exact_match = True)[0])
    with io.BytesIO(source_file_data) as f:
        #Grab the XML file separately while the file is open
        f.seek(8)
        file_entry_name, file_entry_uncompressed_size, file_entry_compressed_size, file_entry_offset, file_entry_flags = struct.unpack("<64sIIII", f.read(64+4+4+4+4))
        xml_file_info_from_header = [file_entry_offset, file_entry_compressed_size, file_entry_uncompressed_size, file_entry_flags]
        file_entry_name, file_entry_uncompressed_size, file_entry_compressed_size, file_entry_offset, file_entry_flags = struct.unpack("<64sIIII", f.read(64+4+4+4+4))
        first_file_after_xml_info_from_header = [file_entry_offset, file_entry_compressed_size, file_entry_uncompressed_size, file_entry_flags] #Also grab info for file 2, for chunking the buffer
        f.seek(xml_file_info_from_header[0])
        xml_file = None
        if xml_file_info_from_header[3] & 1:
            xml_file = uncompress_nislzss(f, xml_file_info_from_header[2], xml_file_info_from_header[1])
        if xml_file_info_from_header[3] & 4:
            xml_file = uncompress_lz4(f, xml_file_info_from_header[2], xml_file_info_from_header[1])
        if xml_file_info_from_header[3] & 8:
            xml_file = uncompress_zstd(f, xml_file_info_from_header[2], xml_file_info_from_header[1])
        patched_file_data = bytearray(source_file_data)

    # Determine XML compression type
    xml_compression_type = int.from_bytes(source_file_data[84:88], "little")
        
    # For filenames of equal length, no offset patching required
    if len(target_string) == len(source_string):
        # Generate the search and substitution strings to inject into the target model
        if sourcefile.split('_')[-1][0] == 'C':
            source_string = sourcefile
            target_string = targetfile
        else:
            source_string = sourcefile.split('_')[0] + '_' + sourcefile.split('_')[1]
            target_string = targetfile.split('_')[0] + '_' + targetfile.split('_')[1]
        xml_offset = int.from_bytes(source_file_data[80:84], "little")
        source_string_offset = patched_file_data.find(bytes(source_string.encode()), xml_offset + 1)
        patched_file_data[source_string_offset:source_string_offset+len(source_string)] = bytes(target_string.encode())

    # If the filenames are of different length, the XML file size will have changed and the file offsets need to change
    if not len(target_string) == len(source_string) and xml_compression_type == 0:
        # Generate the search and substitution strings to inject into the target model
        if sourcefile.split('_')[-1][0] == 'C':
            source_string = '<asset symbol="' + sourcefile + '">'
            target_string = '<asset symbol="' + targetfile + '">'
        else:
            source_string = '<asset symbol="' + sourcefile.split('_')[0] + '_' + sourcefile.split('_')[1] + '">'
            target_string = '<asset symbol="' + targetfile.split('_')[0] + '_' + targetfile.split('_')[1] + '">'
        offset_difference = len(target_string) - len(source_string)

        # Patch model with substitution string
        patched_file_data = bytearray(source_file_data.replace(bytes(source_string, 'ascii'),bytes(target_string, 'ascii')))
        total_offsets = source_file_data[4]
        file_offsets = []
        # Read in all the current file offsets
        for offset in range(total_offsets):
            offset_location = (offset+1)*80
            file_offsets.append(int.from_bytes(source_file_data[offset_location:offset_location+4], "little"))
        # Calculate all the new file offsets
        new_file_offsets = [i + offset_difference for i in file_offsets]
        new_file_offsets[0] = file_offsets[0] # The first offset doesn't actually change
        # Set the new file offsets into the patched file data
        for offset in range(total_offsets):
            offset_location = (offset+1)*80
            offset_bytes = new_file_offsets[offset].to_bytes(4, 'little')
            for intbyte in range(4):
                patched_file_data[offset_location+intbyte] = offset_bytes[intbyte]
        # Calculate and set the new XML file size
        new_xml_size_bytes = (int.from_bytes(source_file_data[72:76], "little") + offset_difference).to_bytes(4, 'little')
        for intbyte in range(4):
            patched_file_data[72+intbyte] = new_xml_size_bytes[intbyte]
            patched_file_data[76+intbyte] = new_xml_size_bytes[intbyte]

    # If the filenames are of different length and the original XML file is compressed, the XML file will need to be replaced.
    if not len(target_string) == len(source_string) and not xml_compression_type == 0:
        # Generate the search and substitution strings to inject into the target model
        if sourcefile.split('_')[-1][0] == 'C':
            source_string = '<asset symbol="' + sourcefile + '">'
            target_string = '<asset symbol="' + targetfile + '">'
        else:
            source_string = '<asset symbol="' + sourcefile.split('_')[0] + '_' + sourcefile.split('_')[1] + '">'
            target_string = '<asset symbol="' + targetfile.split('_')[0] + '_' + targetfile.split('_')[1] + '">'

        # Patch uncompressed XML file with substitution string
        xml_file = bytearray(xml_file.replace(bytes(source_string, 'ascii'),bytes(target_string, 'ascii')))

        # Calculate offset difference for files beyond the XML file
        offset_difference = len(xml_file) - xml_file_info_from_header[1]

        # Split the .pkg file into header, {XML - not needed}, and file archive.
        patched_header = patched_file_data[0:xml_file_info_from_header[0]]
        patched_file_archive = patched_file_data[first_file_after_xml_info_from_header[0]:]

        # Patch the header with all new offsets and new XML file size and compression
        total_offsets = patched_header[4]
        file_offsets = []
        # Read in all the current file offsets
        for offset in range(total_offsets):
            offset_location = (offset+1)*80
            file_offsets.append(int.from_bytes(patched_header[offset_location:offset_location+4], "little"))
        # Calculate all the new file offsets
        new_file_offsets = [i + offset_difference for i in file_offsets]
        new_file_offsets[0] = file_offsets[0] # The first offset doesn't actually change
        # Set the new file offsets into the patched file data
        for offset in range(total_offsets):
            offset_location = (offset+1)*80
            offset_bytes = new_file_offsets[offset].to_bytes(4, 'little')
            for intbyte in range(4):
                patched_header[offset_location+intbyte] = offset_bytes[intbyte]
        # Calculate and set the new XML file size
        patched_header[72:76] = len(xml_file).to_bytes(4, 'little') # Uncompressed size
        patched_header[76:80] = len(xml_file).to_bytes(4, 'little') # Compressed size (no longer compressed)
        patched_header[84:88] = (0).to_bytes(4, 'little') # Set compression flag to 0

        #Reassemble the .pkg file
        patched_file_data = patched_header + xml_file + patched_file_archive

    # Write patched model into target
    with open(targetfile + '.pkg', 'wb') as f:
        f.write(patched_file_data)

    # Clean up memory (probably not necessary)
    del source_file_data
    del patched_file_data
