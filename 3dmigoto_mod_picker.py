# Script to crawl through the Mods folder of a 3DMigoto installation and find mods that conflict
# due to shared 128-bit (short) hashes.  It will ask the user to pick one, and will disable the rest.
# Afterwards, it will rewrite all shaderoverride calls to allow duplicate calling.
# GitHub eArmada8/misc_kiseki

import glob, os, collections

def retrieve_ini_files():
    # Make a list of all ini in the current folder recursively
    return glob.glob('**/*.ini',recursive=True)

def retrieve_hashes(byte_length):
    # Open every ini file and grab every hash
    hashes = []
    ini_filelist = retrieve_ini_files()
    for i in range(len(ini_filelist)):
        with open(ini_filelist[i], 'rb') as f:
            ini_file = f.read()
            current_offset = ini_file.find(b'\x0ahash = ')
            while current_offset > 0:
                line_end = ini_file.find(b'\x0d\x0a',current_offset)
                hashes.append(ini_file[current_offset+8:line_end].decode("utf8"))
                current_offset = ini_file.find(b'\x0ahash = ', current_offset+1)

    # We only want the hashes with matching byte length
    short_hashes = [x for x in hashes if len(x) == byte_length]

    # Remove all unique hashes
    non_unique_hashes = [k for k, v in collections.Counter(short_hashes).items() if v > 1]

    return(non_unique_hashes)

def resolve_mod_conflicts(short_hash):
    # Should be used only for 128-bit (8 byte) hashes
    if not len(short_hash) == 8:
        return(False)
    # Retrieve a list of all the mods that conflict on a given hash
    mod_list = []
    ini_filelist = retrieve_ini_files()
    for i in range(len(ini_filelist)):
        with open(ini_filelist[i], 'rb') as f:
            ini_file = f.read()
            if ini_file.find(short_hash.encode()) > 0:
                mod_list.append(os.path.dirname(os.path.abspath(ini_filelist[i])))

    # Ask the user which mod they would like to keep
    print("The following mods share a common buffer (" + short_hash + "), please choose one to use:\n")
    for i in range(len(mod_list)):
        # To be nice, will add 1 to all indices so the list does not start with zero
        print("[" + str(i+1) + "] " + "".join(mod_list[i].split("\\Mods\\")[-1].split("DISABLED ")))
    try:
        # Subtract 1 from the inputted choice to get the actual list index
        mod_choice = int(input("Please enter the number of the mod to enable: ")) - 1
    except ValueError:
        mod_choice = -1
    while not mod_choice in range(len(mod_list)):
        try:
            # Subtract 1 from the inputted choice to get the actual list index
            mod_choice = int(input("Error, invalid choice.  Please enter the number of the mod to enable: ")) - 1
        except ValueError:
            mod_choice = -1

    # Enable the chosen mod, and disable all others
    for i in range(len(mod_list)):
        if i == mod_choice:
            os.rename(mod_list[i], "\\".join(mod_list[i].split("\\")[:-1]) \
            + "\\" + mod_list[i].split("\\")[-1].split("DISABLED ")[-1])
        else:
            os.rename(mod_list[i], "\\".join(mod_list[i].split("\\")[:-1]) \
            + "\\" + "DISABLED " + mod_list[i].split("\\")[-1].split("DISABLED ")[-1])
    print("Mod conflict successfully resolved.\n")
    return(True)

def replace_shader_commands(ini_file):
    # Open the file
    with open(ini_file, 'rb') as f:
        ini_filedata = f.read()

    # Replace all the ShaderOverride sections commands
    changes_made = False
    current_offset = ini_filedata.find(b'\x0a[ShaderOverride')
    while current_offset > 0:
        line_end = ini_filedata.find(b']\x0d\x0a',current_offset)
        block_end = ini_filedata.find(b'\x0d\x0a[',current_offset)
        hash_line_offset = ini_filedata.find(b'\x0ahash = ',current_offset)
        if (hash_line_offset > 0) and (hash_line_offset < block_end):
            hash = ini_filedata[hash_line_offset+8:ini_filedata.find(b'\x0d\x0a',hash_line_offset)]
            if block_end > 0:
                ini_filedata = ini_filedata[:line_end+3] + b'hash = ' + hash \
                + b'\x0d\x0arun = CommandListActivate\x0d\x0aallow_duplicate_hash = true\x0d\x0a' \
                + ini_filedata[block_end:]
            else:
                ini_filedata = ini_filedata[:line_end+3] + b'hash = ' + hash \
                + b'\x0d\x0arun = CommandListActivate\x0d\x0aallow_duplicate_hash = true\x0d\x0a'
        current_offset = ini_filedata.find(b'\x0a[ShaderOverride', current_offset + 1)
        changes_made = True

    # If any changes were made, write the new file
    if changes_made == True:
        with open(ini_file, 'wb') as f:
            f.write(ini_filedata)

    return(changes_made)

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    # Retrieve mod (short) hashes to process
    non_unique_hashes = retrieve_hashes(8)

    # Resolve each conflict
    for i in range(len(non_unique_hashes)):
        resolve_mod_conflicts(non_unique_hashes[i])

    # Fix all shader calls (by completely rewriting them - all custom commands will be lost)
    ini_files = glob.glob('**/*.ini',recursive=True)
    for i in range(len(ini_files)):
        replace_shader_commands(ini_files[i])

    