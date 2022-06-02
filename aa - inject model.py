# Short script to inject one model in Hajimari no Kiseki into another.  If a source backup exists, it will use the backup
# instead of the existing file.  If no target backup exists, it will create one before erasing the target.
# Commandline: "aa - inject model.py" SOURCE_MODEL.pkg TARGET_MODEL.pkg
# GitHub eArmada8/misc_kiseki

import sys, os, shutil

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    # Grab the name of the source model (model to inject)
    try:
        sourcefile = sys.argv[1].lower()
        if sourcefile[-4:] == '.pkg':
            sourcefile = sourcefile[:-4] # Strip off the '.pkg' if present
        if not os.path.exists(sourcefile + '.pkg'):
            raise Exception('Error: Package "' + sourcefile + '" does not exist!')
    except IndexError:
        sourcefile = str(input("Please enter the name (e.g. C_CHR000_C02) of model to inject: "))
        if sourcefile[-4:] == '.pkg':
            sourcefile = sourcefile[:-4] # Strip off the '.pkg' if present
        while not os.path.exists(sourcefile + '.pkg'):
            sourcefile = str(input("File does not exist.  Please enter the name (e.g. C_CHR000_C02) of model to inject: "))
            if sourcefile[-4:] == '.pkg':
                sourcefile = sourcefile[:-4] # Strip off the '.pkg' if present
    sourcefile = sourcefile.upper()

    # Figure out which file to inject.  If an original file exists, use that file, otherwise use the current file.
    if os.path.exists(sourcefile + '.pkg.original'):
        file_to_inject = sourcefile + '.pkg.original'
    else:
        file_to_inject = sourcefile + '.pkg'

    # Grab the name of the target model (model to be replaced)
    try:
        targetfile = sys.argv[2].lower()
        if targetfile[-4:] == '.pkg':
            targetfile = targetfile[:-4] # Strip off the '.pkg' if present
        if not os.path.exists(targetfile + '.pkg'):
            raise Exception('Error: Package "' + targetfile + '" does not exist!')
    except IndexError:
        targetfile = str(input("Please enter the name (e.g. C_CHR000_C02) of model to replace: "))
        if targetfile[-4:] == '.pkg':
            targetfile = targetfile[:-4] # Strip off the '.pkg' if present
        while not os.path.exists(targetfile + '.pkg'):
            targetfile = str(input("File does not exist.  Please enter the name (e.g. C_CHR000_C02) of model to replace: "))
            if targetfile[-4:] == '.pkg':
                targetfile = targetfile[:-4] # Strip off the '.pkg' if present
    targetfile = targetfile.upper()

    # Check for errors before proceeding
    if not sourcefile.split('_')[-1][0] == targetfile.split('_')[-1][0]:
        # Note: This checks the first character of the last substring when the name is split by underscore.
        # "C_CHR001_C02" will be type "C" and "C_CHR001_FC1" will be type "F"
        # "C_CHR001" will be type "C" which, while not elegant, will work.
        print ('Error: Source and target files are not compatible types!  Press any key to quit.')
        input()
        raise SystemExit()

    # Generate the search and substitution strings to inject into the target model
    if sourcefile.split('_')[-1][0] == 'C':
        source_string = sourcefile
        target_string = targetfile
    else:
        source_string = sourcefile.split('_')[0] + '_' + sourcefile.split('_')[1]
        target_string = targetfile.split('_')[0] + '_' + targetfile.split('_')[1]
    offset_difference = len(target_string) - len(source_string)
    
    # Make a target backup, only if no backup exists.
    if not os.path.exists(targetfile + '.pkg.original'):
        shutil.copy2(targetfile + '.pkg', targetfile + '.pkg.original')

    # Read source model into memory
    with open(file_to_inject, 'rb') as f:
        source_file_data = f.read()
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

    # Code is not yet compatible with changing file name length in compressed XML, this is a placeholder for future code
    if not len(target_string) == len(source_string) and not xml_compression_type == 0:
        print ('Error: Source and target files are not compatible due to XML compression!  Press any key to quit.')
        input()
        raise SystemExit()

    # Write patched model into target
    with open(targetfile + '.pkg', 'wb') as f:
        f.write(patched_file_data)

    # Clean up memory (probably not necessary)
    del source_file_data
    del patched_file_data
