# Short script to inject one model in Hajimari no Kiseki into another.  If a source backup exists, it will use the backup
# instead of the existing file.  If no target backup exists, it will create one before erasing the target.
# GitHub eArmada8/misc_kiseki

import os, shutil

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    # Grab the name of the source model (model to inject)
    sourcefile = str(input("Please enter the name (e.g. C_CHR000_C02) of model to inject: "))
    while not os.path.exists(sourcefile + '.pkg'):
        sourcefile = str(input("File does not exist.  Please enter the name (e.g. C_CHR000_C02) of model to inject: "))
    sourcefile = sourcefile.upper()

    # Figure out which file to inject.  If an original file exists, use that file, otherwise use the current file.
    if os.path.exists(sourcefile + '.pkg.original'):
        file_to_inject = sourcefile + '.pkg.original'
    else:
        file_to_inject = sourcefile + '.pkg'

    # Grab the name of the target model (model to be replaced)
    targetfile = str(input("Please enter the name (e.g. C_CHR000_C02) of model to replace: "))
    while not os.path.exists(targetfile + '.pkg'):
        targetfile = str(input("File does not exist.  Please enter the name (e.g. C_CHR000_C02) of model to replace: "))
    targetfile = targetfile.upper()

    # Check for errors before proceeding
    if sourcefile == targetfile:
        print ('Error: Source and target files are identical!  Press any key to quit.')
        input()
        raise SystemExit()
    if not sourcefile.split('_')[-1][0] == targetfile.split('_')[-1][0]:
        # Note: This checks the first character of the last substring when the name is split by underscore.
        # "C_CHR001_C02" will be type "C" and "C_CHR001_FC1" will be type "F"
        # "C_CHR001" will be type "C" which, while not elegant, will work.
        print ('Error: Source and target files are not compatible types!  Press any key to quit.')
        input()
        raise SystemExit()

    # Generate the search and substitution strings to inject into the target model
    if sourcefile.split('_')[-1][0] == 'C':
        source_string = '<asset symbol="' + sourcefile + '">'
        target_string = '<asset symbol="' + targetfile + '">'
    else:
        source_string = '<asset symbol="' + sourcefile.split('_')[0] + '_' + sourcefile.split('_')[1] + '">'
        target_string = '<asset symbol="' + targetfile.split('_')[0] + '_' + targetfile.split('_')[1] + '">'
    offset_difference = len(target_string) - len(source_string)
    
    # Make a target backup, only if no backup exists.
    if not os.path.exists(targetfile + '.pkg.original'):
        shutil.copy2(targetfile + '.pkg', targetfile + '.pkg.original')

    # Read source model into memory
    with open(file_to_inject, 'rb') as f:
        source_file_data = f.read()

    # Patch model with substitution string
    patched_file_data = bytearray(source_file_data.replace(bytes(source_string, 'ascii'),bytes(target_string, 'ascii')))

    # If the filenames are of different length, the XML file size will have changed and the file offsets need to change
    if not offset_difference == 0:
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

    # Write patched model into target
    with open(targetfile + '.pkg', 'wb') as f:
        f.write(patched_file_data)

    # Clean up memory (probably not necessary)
    del source_file_data
    del patched_file_data

