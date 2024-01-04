# A script to randomize bgm tracks for Trails of Cold Steel IV and into Reverie (NISA).
# Place in {Game Folder}/data/text/dat_en and run.
#
# GitHub eArmada8/misc_kiseki

import struct, os, json, shutil, random
random.seed()

def read_null_terminated_string(f):
    null_term_string = f.read(1)
    while null_term_string[-1] != 0:
        null_term_string += f.read(1)
    return(null_term_string[:-1].decode('utf-8'))

def read_struct_from_json(filename, raise_on_fail = True):
    with open(filename, 'r') as f:
        try:
            return(json.loads(f.read()))
        except json.JSONDecodeError as e:
            print("Decoding error when trying to read JSON file {0}!\r\n".format(filename))
            print("{0} at line {1} column {2} (character {3})\r\n".format(e.msg, e.lineno, e.colno, e.pos))
            if raise_on_fail == True:
                input("Press Enter to abort.")
                raise
            else:
                return(False)

def read_bgm_tbl(table_filename = 't_bgm.tbl'):
    with open(table_filename, 'rb') as f:
        total_entries, num_sections = struct.unpack("<hi",f.read(6))
        section_data = []
        for i in range(num_sections):
            section = {'name': read_null_terminated_string(f),\
                'num_items': struct.unpack("<i", f.read(4))[0]}
            section_data.append(section)
        bgm_table = []
        for i in range(len(section_data)): # Should always be 1, every entry 'bgm'
            for j in range(section_data[i]['num_items']):
                entry_type = read_null_terminated_string(f)
                offset = f.tell()
                block_size, = struct.unpack("<h", f.read(2))
                if entry_type == 'bgm':
                    bgm_entry = {}
                    bgm_entry['id'], = struct.unpack("<h", f.read(2))
                    bgm_entry['track'] = read_null_terminated_string(f)
                    bgm_entry['unk'] = struct.unpack("<3h", f.read(6))
                    bgm_table.append(bgm_entry)
                else:
                    f.seek(block_size,1)
    return(bgm_table)

def write_bgm_tbl(bgm_table, table_filename = 't_bgm.tbl'):
    def nullstr (text):
        return (text.encode('utf-8') + b'\x00')
    table_data = struct.pack("<hi", len(bgm_table), 1)
    table_data += nullstr('bgm') + struct.pack("<i", len(bgm_table))
    for i in range(len(bgm_table)):
        block_data = struct.pack("<h", bgm_table[i]['id'])
        block_data += nullstr(bgm_table[i]['track'])
        block_data += struct.pack("<3h", *bgm_table[i]['unk'])
        table_data += nullstr('bgm') + struct.pack("<h", len(block_data)) + block_data
    with open(table_filename,'wb') as f:
        f.write(table_data)
    return

def randomize_bgm(bgm_table, db_entry):
    #Should always be only one entry, but just in case of weird duplicates...
    table_entries = [i for i in range(len(bgm_table)) if bgm_table[i]['id'] == db_entry['id']]
    for k in table_entries:
        bgm_table[k] = {'id': bgm_table[k]['id'],\
            'track': db_entry['options'][random.randrange(len(db_entry['options']))],\
            'unk': bgm_table[k]['unk']}
    return(bgm_table)

def randomize_bgms(bgm_table, random_db):
    for i in range(len(random_db)):
        bgm_table = randomize_bgm(bgm_table, random_db[i])
    return(bgm_table)

def process_tbl(table_filename = 't_bgm.tbl', random_db_filename = 't_bgm_options.json'):
    # Make a backup, only if no backup exists.
    if not os.path.exists(table_filename + '.original'):
        shutil.copy2(table_filename, table_filename + '.original')
    # Read the randomizer options
    random_db = read_struct_from_json(random_db_filename)
    bgm_table = read_bgm_tbl(table_filename)
    bgm_table = randomize_bgms(bgm_table, random_db)
    write_bgm_tbl(bgm_table, table_filename)

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    process_tbl()