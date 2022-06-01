# Character table decoder - will decode t_name.tbl in the current folder and output table.csv
# GitHub eArmada8/misc_kiseki

import os

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    with open('t_name.tbl', 'rb') as f:
        source_file_data = f.read()

    current_offset = 6 #Skip first offset
    model_list = []
    while current_offset > 0:
        # Advance to the next offset
        current_offset = source_file_data.find(b'NameTableData', current_offset + 1)
        # Find the next offset, only to use for finding the end of the current buffer
        next_offset = source_file_data.find(b'NameTableData', current_offset + 1)
        current_buffer = source_file_data[(current_offset+18):next_offset]
        current_buffer = current_buffer[0:current_buffer.find(b'\x00\x00\x00')].replace(b'\x00', b',')
        # Removes a strange sequence that is occasionally in the text in fan-translated Hajimari, comment out if not needed
        current_buffer = current_buffer.replace(b'\xe2\x98\x86', b' ')
        model_list.append(str(current_buffer, 'utf-8') + '\n')

    savedata = "".join(model_list)
    with open('table.csv', 'wb') as f:
        f.write(savedata.encode('utf-8'))
