# Small utility to find 3DMigoto mods that have a matching hash file.  Run this in your mod
# folder, type in the hash, and it will find all the ini files that have that hash.  Meant to 
# help track down mods that are causing silent errors, etc.  (For example if a mesh is missing or
# modified that you did not expect, you can find its hash in hunting mode, and use this to figure
# out which mod is changing that hash.
#
# GitHub eArmada8/misc_kiseki

import os, sys, glob, re

def retrieve_ini_files():
    # Make a list of all ini in the current folder recursively
    return glob.glob('**/*.ini',recursive=True)

def find_file_by_hash(search_hash):
    # Sanitize input (remove all non-hexadecimal characters, make lower case)
    search_hash = re.sub(r'[^a-fA-F0-9]','', search_hash).lower()
    matches = []
    # Open every ini file and grab every hash
    ini_filelist = retrieve_ini_files()
    for i in range(len(ini_filelist)):
        with open(ini_filelist[i], 'rb') as f:
            ini_file = f.read()
            current_offset = ini_file.find(b'\x0ahash = ')
            while current_offset > 0:
                line_end = ini_file.find(b'\x0d\x0a',current_offset)
                if ini_file[current_offset+8:line_end].decode("utf8") == search_hash:
                    matches.append(ini_filelist[i])
                current_offset = ini_file.find(b'\x0ahash = ', current_offset+1)
    return(matches)

if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    # If argument given, attempt to search for argument
    if len(sys.argv) > 1:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('search_hash', help="Hexadecimal 3DMigoto hash to search for (e.g. deadb33f).")
        args = parser.parse_args()
        matches = find_file_by_hash(args.search_hash)
        print("Results:")
        for i in range(len(matches)):
            print(matches[i])
    else:
        search_hash = input("\nPlease enter hexadecimal 3DMigoto hash to search for (e.g. deadb33f):  ")
        if search_hash != re.sub(r'[^a-fA-F0-9]','', search_hash):
            while search_hash != re.sub(r'[^a-fA-F0-9]','', search_hash):
                search_hash = input("\nInvalid input.  Please enter hexadecimal 3DMigoto hash to search for (e.g. deadb33f):  ")
        matches = find_file_by_hash(search_hash)
        print("Results:")
        for i in range(len(matches)):
            print(matches[i])
        input("Press Enter to Quit")
