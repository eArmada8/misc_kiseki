# A script to find and resolve DLC item ID conflicts for Trails of Cold Steel III, IV and into Reverie (NISA).
# Place in the base directory of the game (the folder with both bin and data folders within it) and run.
#
# GitHub eArmada8/misc_kiseki

import struct, os, glob, sys

def read_null_terminated_string(f):
    null_term_string = f.read(1)
    while null_term_string[-1] != 0:
        null_term_string += f.read(1)
    return(null_term_string[:-1].decode('utf-8'))

# Should be the table with Tear Balm
def detect_ed8_game():
    game_type = 0
    if os.path.exists('data/text/'):
        item_tables = glob.glob('data/text/**/t_item_en.tbl', recursive = True) \
            + glob.glob('data/text/**/t_item.tbl', recursive = True) \
            + glob.glob('data/dlc/**/t_item.tbl', recursive = True)
    else:
        return(-1) # Not in a ed8 root directory
    for i in range(len(item_tables)):
        tear_balm_found = False
        with open(item_tables[i], 'rb') as f:
            total_entries, num_sections = struct.unpack("<hi",f.read(6))
            section_data = []
            for j in range(num_sections):
                section = {'name': read_null_terminated_string(f),\
                    'num_items': struct.unpack("<i", f.read(4))[0]}
                section_data.append(section)
            for j in range(len(section_data)):
                for k in range(section_data[j]['num_items']):
                    entry_type = read_null_terminated_string(f)
                    block_size, = struct.unpack("<h", f.read(2))
                    item_num, = struct.unpack("<h", f.read(2))
                    if item_num == 0:
                        item_block_start_offset = f.tell()-2
                        item_block = f.read(block_size-2)
                        item_block_name_offset = item_block.find(b'Tear')
                        if item_block_name_offset - item_block_start_offset in [0x68, 0x7f, 0x6b]:
                            tear_balm_found = True
                            game_type = {0x68:3, 0x7f:4, 0x6b:5}[item_block_name_offset - item_block_start_offset]
                    else:
                        f.seek(block_size-2,1)
                    if tear_balm_found:
                        break
                if tear_balm_found:
                    break
        if tear_balm_found:
            break
    if game_type not in [3,4,5]:
        game_input_raw = input("Game type detection failed (likely non-NISA CS3/CS4/Reverie).  Try with manual type?  Input 3, 4 or 5.  ")
        try:
            game_input = int(game_input_raw)
            if game_input in [3,4,5]:
                game_type = game_input
                print("\nAttempting to parse using {0} table format.".format({3:'CS3', 4:'CS4', 5:'Reverie'}[game_type]))
                print("If the item names are not correct, do not attempt to use!\n")
        except ValueError:
            pass
    return(game_type)

def read_id_numbers_with_offsets(table):
    item_numbers = {}
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
                offset = f.tell()
                block_size, = struct.unpack("<h", f.read(2))
                item_num, = struct.unpack("<h", f.read(2))
                item_numbers[item_num] = {'table': table, 'entry_type': entry_type, 'offset': offset}
                f.seek(block_size-2,1)
    return(item_numbers)

def get_all_id_numbers(item_tables):
    all_item_numbers = {}
    for i in range(len(item_tables)):
        all_item_numbers.update({x:item_tables[i] for x in read_id_numbers_with_offsets(item_tables[i]).keys()})
    return(all_item_numbers)

def get_item_name_by_item_entry(item_entry, game_type = 0):
    if game_type in [3,4,5]:
        with open(item_entry['table'], 'rb') as f:
            f.seek(item_entry['offset'] + 6,0)
            read_null_terminated_string(f) #Flags
            f.seek({3:0x7f, 4:0x96, 5:0x8d}[game_type],1)
            item_name = read_null_terminated_string(f)
        return(item_name)
    else:
        return("")

def replace_item_id_in_t_item (table, old_id, new_id):
    with open(table, 'r+b') as f:
        total_entries, num_sections = struct.unpack("<hi",f.read(6))
        section_data = []
        for i in range(num_sections):
            section = {'name': read_null_terminated_string(f),\
                'num_items': struct.unpack("<i", f.read(4))[0]}
            section_data.append(section)
        for i in range(len(section_data)):
            for j in range(section_data[i]['num_items']):
                entry_type = read_null_terminated_string(f)
                offset = f.tell()
                block_size, item_num = struct.unpack("<2h", f.read(4))
                if item_num == old_id:
                    f.seek(-2,1)
                    f.write(struct.pack("<h", new_id))
                f.seek(offset + 2 + block_size,0)
    return

def replace_item_id_in_t_attach (table, old_id, new_id):
    with open(table, 'r+b') as f:
        total_entries, num_sections = struct.unpack("<hi",f.read(6))
        section_data = []
        for i in range(num_sections):
            section = {'name': read_null_terminated_string(f),\
                'num_items': struct.unpack("<i", f.read(4))[0]}
            section_data.append(section)
        for i in range(len(section_data)):
            for j in range(section_data[i]['num_items']):
                entry_type = read_null_terminated_string(f)
                offset = f.tell()
                block_size, chr_id, item_type, unk0, item_num = struct.unpack("<5h", f.read(10))
                if item_num == old_id:
                    f.seek(-2,1)
                    f.write(struct.pack("<h", new_id))
                f.seek(offset + 2 + block_size,0)
    return

def replace_item_id_in_t_dlc (table, old_id, new_id, game_type = 0):
    if game_type in [3,4,5]:
        with open(table, 'r+b') as f:
            total_entries, num_sections = struct.unpack("<hi",f.read(6))
            section_data = []
            for i in range(num_sections):
                section = {'name': read_null_terminated_string(f),\
                    'num_items': struct.unpack("<i", f.read(4))[0]}
                section_data.append(section)
            for i in range(len(section_data)):
                for j in range(section_data[i]['num_items']):
                    entry_type = read_null_terminated_string(f)
                    offset = f.tell()
                    block_size, dlc_id = struct.unpack("<2h", f.read(4))
                    f.seek(6,1)
                    if game_type > 3:
                        f.seek(12,1)
                    name = read_null_terminated_string(f)
                    desc = read_null_terminated_string(f)
                    item_struct_offset = f.tell()
                    current_items = [list(struct.unpack("<2h",f.read(4))) for x in range(20)]
                    if old_id in [x[0] for x in current_items]:
                        f.seek(item_struct_offset,0)
                        f.write(struct.pack("<40h",\
                            *[x for y in [x if not x[0] == old_id else [new_id,x[1]] for x in current_items] for x in y]))
                    f.seek(offset + 2 + block_size,0)
    return

def replace_item_id(dlc_id, old_id, new_id, game_type = 0):
    item_tables = glob.glob('data/dlc/text/{:04d}/**/t_item.tbl'.format(dlc_id), recursive = True)
    for i in range(len(item_tables)):
        replace_item_id_in_t_item(item_tables[i], old_id, new_id)
    attach_tables = glob.glob('data/dlc/text/{:04d}/**/t_attach.tbl'.format(dlc_id), recursive = True)
    for i in range(len(attach_tables)):
        replace_item_id_in_t_attach(attach_tables[i], old_id, new_id)
    dlc_tables = glob.glob('data/dlc/text/{:04d}/**/t_dlc.tbl'.format(dlc_id), recursive = True)
    for i in range(len(dlc_tables)):
        replace_item_id_in_t_dlc(dlc_tables[i], old_id, new_id, game_type)
    return

def resolve_dlc(allow_low_numbers = False):
    game_type = detect_ed8_game()
    if os.path.exists('data/text/'):
        item_tables = glob.glob('data/text/**/t_item_en.tbl', recursive = True)
        if len(item_tables) < 1:
            item_tables = glob.glob('data/text/**/t_item.tbl', recursive = True)
            if len(item_tables) < 1:
                input("No master item table found, is this script in the root game folder?")
            else:
                item_tables = [item_tables[0]]
        else:
            item_tables = [item_tables[0]]
        #In reading DLC tables, default to English, otherwise the first option available (usually dat)
        dats = [x.replace('\\','/').split('/')[-1] for x in glob.glob(glob.glob('data/dlc/text/*')[0]+'/*')]
        if 'dat_en' in dats:
            dat_name = 'dat_en'
        else:
            dat_name = dat[0]
        item_tables.extend(sorted(glob.glob('data/dlc/**/{0}/t_item.tbl'.format(dat_name), recursive = True)))
    else:
        input("No master item table found, is this script in the root game folder?")
    #Evaluate for conflicts, one table at a time
    all_utilized_item_ids = sorted(list(get_all_id_numbers(item_tables).keys()))
    dlc_ids = sorted(list(get_all_id_numbers(item_tables[1:]).keys()))
    valid_items = []
    for i in range(len(item_tables)):
        current_table_items = read_id_numbers_with_offsets(item_tables[i])
        if any([x in valid_items for x in list(current_table_items.keys())]):
            # There is a conflict, find the conflicts and address them one at a time
            conflicts = [x for x in list(current_table_items.keys()) if x in valid_items]
            all_prior_entries = get_all_id_numbers(item_tables[0:i])
            for j in range(len(conflicts)):
                print("Conflict found in {0}, item {1} assigned to {2}.".format(item_tables[i].replace('\\','/'),\
                    conflicts[j], get_item_name_by_item_entry(current_table_items[conflicts[j]], game_type)))
                print("However that item_id is already in use in {0} as {1}.".format(all_prior_entries[conflicts[j]].replace('\\','/'),\
                    get_item_name_by_item_entry(read_id_numbers_with_offsets(all_prior_entries[conflicts[j]])[conflicts[j]], game_type)))
                if allow_low_numbers:
                    next_available = [x for x in range(max(all_utilized_item_ids)) if x not in all_utilized_item_ids][0]
                else:
                    next_available = [x for x in range(min(dlc_ids), max(all_utilized_item_ids)) if x not in all_utilized_item_ids][0]
                print("Item ID {0} is available, assign {0} to which item? (Do not pick official Falcom items!)".format(next_available))
                print("1. {0} (Table {1})".format(get_item_name_by_item_entry(current_table_items[conflicts[j]], game_type), \
                    int(item_tables[i].replace('\\','/').split('/')[3])))
                allowed_changes = [0,1]
                # Check if conflict is in DLC table; if yes then either table can be changed, if no then only the current table can be changed.
                if len(all_prior_entries[conflicts[j]].replace('\\','/').split('/')) > 4:
                    print("2. {0} (Table {1})".format(get_item_name_by_item_entry(read_id_numbers_with_offsets(all_prior_entries[conflicts[j]])[conflicts[j]], game_type),\
                        int(all_prior_entries[conflicts[j]].replace('\\','/').split('/')[3])))
                    allowed_changes.append(2)
                print("0. Skip")
                table_to_fix = -1
                while table_to_fix not in allowed_changes:
                    table_to_fix_input = input("Please enter which item should be changed: ")
                    try:
                        table_to_fix = int(table_to_fix_input)
                        if table_to_fix not in allowed_changes:
                            print("Invalid entry!")
                    except ValueError:
                        print("Invalid entry!")
                if table_to_fix == 1:
                    print("Replacing item ID {0} with {1} in DLC {2}.\n".format(conflicts[j], next_available, item_tables[i].replace('\\','/').split('/')[3]))
                    replace_item_id(int(item_tables[i].replace('\\','/').split('/')[3]), conflicts[j], next_available, game_type)
                    all_utilized_item_ids.append(next_available)
                elif table_to_fix == 2:
                    print("Replacing item ID {0} with {1} in DLC {2}.\n".format(conflicts[j], next_available, all_prior_entries[conflicts[j]].replace('\\','/').split('/')[3]))
                    replace_item_id(int(all_prior_entries[conflicts[j]].replace('\\','/').split('/')[3]), conflicts[j], next_available, game_type)
                    all_utilized_item_ids.append(next_available)
                else:
                    print("Skipping item ID {0}.".format(conflicts[j]))
        valid_items.extend(list(read_id_numbers_with_offsets(item_tables[i]).keys()))
    input("Done resolving all conflicts!  Press Enter to quit.")
    return

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    resolve_dlc()