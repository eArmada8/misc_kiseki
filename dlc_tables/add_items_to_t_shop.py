# A script to add entries to t_shop.tbl for CS3, CS4, Trails into Reverie.  Put the original t_shop.tbl in the folder
# as t_shop.tbl.original, and put .json files (from make_dlc_tbls.py) in folders named by shop_id (for example, in a folder
# named 1041 for the reverie corridor costume shop, which is shop_id 1041).
#
# GitHub eArmada8/misc_kiseki

import json, glob, os, sys, struct

def read_null_terminated_string(f):
    null_term_string = f.read(1)
    while null_term_string[-1] != 0:
        null_term_string += f.read(1)
    return(null_term_string[:-1].decode('utf-8'))

def read_id_numbers_with_offsets(table):
    table_data = []
    with open(table, 'rb') as f:
        f.seek(0,2)
        file_end = f.tell()
        f.seek(0,0)
        total_entries, num_sections = struct.unpack("<hi",f.read(6))
        section_data = []
        for i in range(num_sections):
            section = {'name': read_null_terminated_string(f),\
                'num_items': struct.unpack("<i", f.read(4))[0]}
            section_data.append(section)
        while f.tell() < file_end:
            entry_type = read_null_terminated_string(f)
            offset = f.tell()
            block_size, = struct.unpack("<h", f.read(2))
            block_data = f.read(block_size)
            table_data.append({'type': entry_type, 'data': block_data})
    return(table_data, section_data)

def read_shop_id_numbers (table_data):
    return([struct.unpack('<H',x['data'][0:2])[0] if x['type'] == 'ShopItem' else -1 for x in table_data])

def read_items():
    def read_json_for_item_id(json_file):
        with open(json_file, 'rb') as f:
            data = json.loads(f.read())
            if 'item_id' in data:
                return(data['item_id'])
            else:
                return(-1)
    new_items_json_list = glob.glob('**/*.json',recursive=True)
    return([{'shop_id': int(x.replace('\\','/').split('/')[0]), 'item_id': read_json_for_item_id(x)} for x in new_items_json_list])

def build_shop_item(shop_id, item_id):
    entry = struct.pack('<4H', shop_id, item_id, 9999, 0)
    entry += struct.pack('<B4H', 0, 0, 0, 65535, 0)
    return({'type':'ShopItem','data':entry})

def add_items_to_table(table_data, new_items):
    new_item_dict = {x:[y for y in new_items if y['shop_id'] == x] for x in list(set([z['shop_id'] for z in new_items]))}
    for shop_id in new_item_dict:
        # Parsing the table every time is admittedly not efficient, but once per shop isn't bad
        shop_id_column = read_shop_id_numbers(table_data)
        if shop_id in shop_id_column:
            #Find the index of the *last* item in the shop
            insertion = len(shop_id_column)-shop_id_column[::-1].index(shop_id)
        else:
            #Append to the end of the list
            insertion = len(shop_id_column)
        for i in range(len(new_item_dict[shop_id])):
            table_data.insert(insertion+i, build_shop_item(new_item_dict[shop_id][i]['shop_id'], new_item_dict[shop_id][i]['item_id']))
    return(table_data)

def generate_table(table_data, section_data):
    if not all([x['type'] in [x['name'] for x in section_data] for x in table_data]):
        input("Attempting to add sections that do not belong!  Is the original table correct?  Press Enter to abort.")
        raise
    section_counts = {x['name']:0 for x in section_data}
    table_block_data = b''
    for i in range(len(table_data)):
        table_block_data += table_data[i]['type'].encode() + b'\x00' + struct.pack('<H', len(table_data[i]['data'])) + table_data[i]['data']
        section_counts[table_data[i]['type']] += 1
    table_header_data = b''
    for k in section_counts:
        table_header_data += k.encode() + b'\x00' + struct.pack('<i', section_counts[k])
    return(struct.pack('<hi', len(table_data), len(section_counts)) + table_header_data + table_block_data)

def process_tbl (table = 't_shop.tbl'):
    original_table = table + '.original'
    table_data, section_data = read_id_numbers_with_offsets(original_table)
    table_data = add_items_to_table(table_data, read_items())
    with open(table, 'wb') as f:
        f.write(generate_table(table_data, section_data))

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    process_tbl('t_shop.tbl')
