# Short script to inject one model in Kuro no Kiseki into another.  If a source backup exists, it will use the backup
# instead of the existing file.  If no target backup exists, it will create one before erasing the target.
# GitHub eArmada8/misc_kiseki

import sys, os, shutil

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    # Grab the name of the source model (model to inject)
    try:
        sourcefile = sys.argv[1].lower()
        if sourcefile[-4:] == '.mdl':
            sourcefile = sourcefile[:-4] # Strip off the '.mdl' if present
        if not os.path.exists(sourcefile + '.mdl'):
            raise Exception('Error: Package "' + sourcefile + '" does not exist!')
    except IndexError:
        sourcefile = str(input("Please enter the name (e.g. chr0000_c02) of model to inject: "))
        if sourcefile[-4:] == '.mdl':
            sourcefile = sourcefile[:-4] # Strip off the '.mdl' if present
        while not os.path.exists(sourcefile + '.mdl'):
            sourcefile = str(input("File does not exist.  Please enter the name (e.g. chr0000_c02) of model to inject: "))
            if sourcefile[-4:] == '.mdl':
                sourcefile = sourcefile[:-4] # Strip off the '.mdl' if present
    sourcefile = sourcefile.lower()

    # Figure out which file to inject.  If an original file exists, use that file, otherwise use the current file.
    if os.path.exists(sourcefile + '.mdl.original'):
        file_to_inject = sourcefile + '.mdl.original'
    else:
        file_to_inject = sourcefile + '.mdl'

    # Grab the name of the target model (model to be replaced)
    try:
        targetfile = sys.argv[2].lower()
        if targetfile[-4:] == '.mdl':
            targetfile = targetfile[:-4] # Strip off the '.mdl' if present
        if not os.path.exists(targetfile + '.mdl'):
            raise Exception('Error: Package "' + targetfile + '" does not exist!')
    except IndexError:
        targetfile = str(input("Please enter the name (e.g. chr0000_c02) of model to replace: "))
        if targetfile[-4:] == '.mdl':
            targetfile = targetfile[:-4] # Strip off the '.mdl' if present
        while not os.path.exists(targetfile + '.mdl'):
            targetfile = str(input("File does not exist.  Please enter the name (e.g. chr0000_c02) of model to replace: "))
            if targetfile[-4:] == '.mdl':
                targetfile = targetfile[:-4] # Strip off the '.mdl' if present
    targetfile = targetfile.lower()

    # Check for errors before proceeding
    if not sourcefile.split('_')[-1][0] == targetfile.split('_')[-1][0]:
        # Note: This checks the first character of the last substring when the name is split by underscore.
        # "chr0001_c02" will be type "c" and "chr001_face" will be type "f"
        # "chr0001" will be type "c" which, while not elegant, will work (sufficiently.
        print ('Error: Source and target files are not compatible types!  Press any key to quit.')
        input()
        raise SystemExit()

    # Make a target backup, only if no backup exists.
    if not os.path.exists(targetfile + '.mdl.original'):
        shutil.copy2(targetfile + '.mdl', targetfile + '.mdl.original')

    # Read source model into memory
    with open(file_to_inject, 'rb') as f:
        source_file_data = f.read()

    with open(targetfile + '.mdl', 'wb') as f:
        f.write(source_file_data)

    # Clean up memory (probably not necessary)
    del source_file_data
