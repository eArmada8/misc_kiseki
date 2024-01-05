# Short script to extract data from a set of dlc tables made by make_dlc_tbls.py for
# Trails of Cold Steel III / IV / into Reverie and output them as JSON files.
#
# GitHub eArmada8/misc_kiseki

import struct, json, os

def read_null_terminated_string(f):
    null_term_string = f.read(1)
    while null_term_string[-1] != 0:
        null_term_string += f.read(1)
    return(null_term_string[:-1].decode('utf-8'))

def input_gametype():
    game_type = 0
    while game_type not in [3,4,5]:
        game_type_raw = input("Which game? [3=CS3, 4=CS4, 5=NISA Reverie, leave blank for 4] ")
        if game_type_raw == '':
            game_type = 4
        else:
            try:
                game_type = int(game_type_raw)
                if game_type not in [3,4,5]:
                    print("Invalid entry!")
            except ValueError:
                print("Invalid entry!")
    return(game_type)

def read_dlc_table(dlc_table, game_type = 4):
    dlcs = []
    with open(dlc_table, 'rb') as f:
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
                if section_data[i]['name'] == 'dlc':
                    dlc = {}
                    dlc['dlc_id'], dlc['dlc_sort_id'] = struct.unpack("<2h", f.read(4))
                    if game_type == 3:
                        f.seek(4,1)
                    else:
                        f.seek(16,1)
                    dlc['dlc_name'] = read_null_terminated_string(f)
                    dlc['dlc_desc'] = read_null_terminated_string(f)
                    dlc['items'] = []
                    for k in range(20):
                        dlc['items'].append(list(struct.unpack("<2h", f.read(4))))
                    dlcs.append(dlc)
                else:
                    f.seek(block_size,1)
    return(dlcs)

def read_attach_table(attach_table, game_type = 4):
    attachdata = []
    with open(attach_table, 'rb') as f:
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
                if section_data[i]['name'] == 'AttachTableData':
                    attach = {}
                    attach['char_id'], attach['item_type'], unk0, attach['item_id'] = struct.unpack("<4h", f.read(8))
                    if game_type == 3:
                        f.seek(14,1)
                    else:
                        f.seek(8,1)
                        attach['rev_voice_flag'], attach['item_cs4rev_scraft_cutin'] = struct.unpack("<2i", f.read(8))
                        f.seek(2,1)
                        pkg_name = read_null_terminated_string(f)
                    attach['model'] = read_null_terminated_string(f)
                    attach['attach_point'] = read_null_terminated_string(f)
                    attachdata.append(attach)
                else:
                    f.seek(block_size,1)
    return(attachdata)

# Currently only supports item, not item_q or item_e
def read_item_table(item_table, game_type = 4):
    items = []
    with open(item_table, 'rb') as f:
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
                if section_data[i]['name'] == 'item':
                    item = {}
                    item['item_id'], item['chr_id'] = struct.unpack("<2h", f.read(4))
                    if game_type == 5:
                        f.seek(4,1)
                        item['item_type'], = struct.unpack("<H", f.read(2))
                        f.seek(9,1)
                        item['target_type'], = struct.unpack("<B", f.read(1))
                        f.seek(123,1)
                        item['item_sort_id'], = struct.unpack("<H", f.read(2))
                        f.seek(2,1)
                    elif game_type == 4:
                        f.seek(4,1)
                        item['item_type'], = struct.unpack("<H", f.read(2))
                        f.seek(8,1)
                        item['target_type'], = struct.unpack("<B", f.read(1))
                        f.seek(133,1)
                        item['item_sort_id'], = struct.unpack("<H", f.read(2))
                        f.seek(2,1)
                    elif game_type == 3:
                        f.seek(2,1)
                        item['item_type'], = struct.unpack("<H", f.read(2))
                        f.seek(8,1)
                        item['target_type'], = struct.unpack("<B", f.read(1))
                        f.seek(112,1)
                        item['item_sort_id'], = struct.unpack("<H", f.read(2))
                        f.seek(2,1)
                    item['item_name'] = read_null_terminated_string(f)
                    item['item_desc'] = read_null_terminated_string(f)
                    if game_type in [3,4]:
                        f.seek(8,1)
                    items.append(item)
                else:
                    f.seek(block_size,1)
    return(items)

def write_struct_to_json(struct, filename):
    if not filename[:-5] == '.json':
        filename += '.json'
    with open(filename, "wb") as f:
        f.write(json.dumps(struct, indent=4).encode("utf-8"))
    return

def write_dlc_json(dlcs, game_type):
    for i in range(len(dlcs)):
        write_struct_to_json({'game_type': game_type,\
            'dlc_id': dlcs[i]['dlc_id'], 'dlc_sort_id': dlcs[i]['dlc_sort_id'],\
            'dlc_name': dlcs[i]['dlc_name'], 'dlc_desc': dlcs[i]['dlc_desc']},\
            'dlc{}'.format(str(i) if i > 0 else ''))
    return

def write_pkg_jsons(attaches, items, dlcs):
    packages = list(set([x['model'] for x in attaches]))
    for i in range(len(packages)):
        attach = attaches[[j for j in range(len(attaches)) if attaches[j]['model'] == packages[i]][0]]
        matching_items = [j for j in range(len(items)) if items[j]['item_id'] == attach['item_id']]
        if len(matching_items) > 0:
            item = items[matching_items[0]]
            matching_dlcs = [x for x in dlcs if item['item_id'] in [y for z in x['items'] for y in z]]
            if len(matching_dlcs) > 0:
                item_quantity = sum([x[1] for x in matching_dlcs[0]['items'] if x[0] == item['item_id']])
                write_struct_to_json({'item_id': item['item_id'],\
                    'item_type': item['item_type'], 'item_name': item['item_name'], 'item_desc': item['item_desc'],\
                    'target_type': item['target_type'], 'attach_point': attach['attach_point'],\
                    'chr_id': item['chr_id'], 'chr_id_a': attach['char_id'], 'item_sort_id': item['item_sort_id'],\
                    'item_cs4rev_scraft_cutin': (item['item_cs4rev_scraft_cutin'] if 'item_cs4rev_scraft_cutin' in item else 0),\
                    'rev_voice_flag': (item['rev_voice_flag'] if 'rev_voice_flag' in item else 0),\
                    'item_quantity': item_quantity},
                    packages[i]+'.pkg')

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    game_type = input_gametype()
    dlcs = read_dlc_table('t_dlc.tbl', game_type)
    attaches = read_attach_table('t_attach.tbl', game_type)
    items = read_item_table('t_item.tbl', game_type)
    write_dlc_json(dlcs, game_type)
    write_pkg_jsons(attaches, items, dlcs)