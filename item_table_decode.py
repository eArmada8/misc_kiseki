# Character table decoder - will decode t_name.tbl in the current folder and output table.csv
# GitHub eArmada8/misc_kiseki

import os, struct, csv
from collections import OrderedDict

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    with open('t_item.tbl', 'rb') as f:
        source_file_data = f.read()

    current_offset = 26 #Skip first offset
    item_list = {}
    while current_offset > 0:
        item_id = -1
        item_name = b''
        # Advance to the next offset
        current_offset = source_file_data.find(b'item', current_offset + 1)
        # Find the next offset, only to use for finding the end of the current buffer
        next_offset = source_file_data.find(b'item', current_offset + 1)
        current_buffer = source_file_data[current_offset:next_offset]
        if (current_buffer[0:6] == b'item_q'):
            try:
                item_id = struct.unpack("<h", current_buffer[9:11])[0]
            except:
                pass
        else:
            try:
                item_id = struct.unpack("<h", current_buffer[7:9])[0]
            except:
                pass
        try:
            item_name = current_buffer[80:].split(b'\xff\xff')[1].split(b'\x00')[0]
        except:
            pass
        item_name = str(item_name, 'utf-8')
        item_list[item_id] = item_name

    sorted_item_list = dict(sorted(item_list.items(), key=lambda item: item[1]))

    with open('item_table.csv', 'wb') as f:
        for key in sorted_item_list.keys():
            f.write(str(key).encode('utf8')+b',"'+item_list[key].replace('"','""').encode('utf8')+'"\r\n'.encode('utf8'))

    with open('item_table_for_CE_lua.txt', 'wb') as f:
        for key in sorted_item_list.keys():
            f.write(b'"'+str(key).encode('utf8')+b':'+item_list[key].replace('"','\\"').encode('utf8')+'",\r\n'.encode('utf8'))
