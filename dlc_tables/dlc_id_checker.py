# Script to check if an ID number is in use for Trails of Cold Steel 3, 4, Reverie.
# Usage: Place in the root directory of the game (same folder that bin and data folders are in)
#        and run.
# GitHub eArmada8/misc_kiseki

import struct, os, glob, sys

def read_null_terminated_string(f):
    null_term_string = f.read(1)
    while null_term_string[-1] != 0:
        null_term_string += f.read(1)
    return(null_term_string[:-1].decode('utf-8'))

def read_id_numbers(table):
    item_numbers = []
    with open(table, 'rb') as f:
        total_entries, num_sections = struct.unpack("<hi",f.read(6))
        section_data = []
        for i in range(num_sections):
            section = {'name': read_null_terminated_string(f),\
                'num_items': struct.unpack("<i", f.read(4))[0]}
            section_data.append(section)
        for i in range(len(section_data)):
            for j in range(section_data[i]['num_items']):
                entry_type = read_null_terminated_string(f)
                block_size, = struct.unpack("<h", f.read(2))
                item_num, = struct.unpack("<h", f.read(2))
                item_numbers.append(item_num)
                f.seek(block_size-2,1)
    return(item_numbers)

def get_all_id_numbers():
    if os.path.exists('data/text/'):
        item_tables = glob.glob('data/dlc/**/t_dlc.tbl', recursive = True)
    all_item_numbers = []
    for i in range(len(item_tables)):
        print("Checking {0}...".format(item_tables[i]))
        all_item_numbers.extend(read_id_numbers(item_tables[i]))
    return(sorted(list(set(all_item_numbers))))

def check_id_number(all_item_numbers, number = -1):
    while number == -1:
        print("The current range of ID numbers is {0} to {1}.".format(min(all_item_numbers), max(all_item_numbers)))
        number_input = input("What number would you like to check? ")
        try:
            number = int(number_input)
        except ValueError:
            print("Invalid Entry!")
    return(number in all_item_numbers)

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    all_item_numbers = get_all_id_numbers()
    if len(sys.argv) > 1:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('id_num', help="ID Number to check.")
        args = parser.parse_args()
        if check_id_number(all_item_numbers, int(args.id_num)):
            print("Item ID {0} already exists!".format(int(args.id_num)))
        else:
            print("Item ID {0} does not exist!".format(int(args.id_num)))
    else:
        number = -1
        while number == -1:
            print("The current range of ID numbers is {0} to {1}.".format(min(all_item_numbers), max(all_item_numbers)))
            number_input = input("What number would you like to check? (Press enter to quit) ")   
            if number_input == '':
                break
            else:
                try:
                    number = int(number_input)
                    if check_id_number(all_item_numbers, number):
                        print("Item ID {0} already exists!".format(number))
                    else:
                        print("Item ID {0} does not exist!".format(number))
                    number = -1
                except ValueError:
                    print("Invalid Entry!")