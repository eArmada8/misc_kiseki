# Short script to inject one model in Hajimari no Kiseki into another.  If a source backup exists, it will use the backup instead of the existing file.  If no target backup exists, it will create one before erasing the target.
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

    # Make a target backup, only if no backup exists.
    if not os.path.exists(targetfile + '.pkg.original'):
        shutil.copy2(targetfile + '.pkg', targetfile + '.pkg.original')

    # Read source model into memory
    with open(file_to_inject, 'rb') as f:
        source_file_data = f.read()

    # Patch model with substitution string
    patched_file_data = source_file_data.replace(bytes(source_string, 'ascii'),bytes(target_string, 'ascii'))

    # Write patched model into target
    with open(targetfile + '.pkg', 'wb') as f:
        f.write(patched_file_data)

    # Clean up memory (probably not necessary)
    del source_file_data
    del patched_file_data

