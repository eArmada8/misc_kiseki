# Kuro Item table decoder - will decode t_item.json in the current folder and output item_table.csv as well
# as a lua array for cheat engine.  Use Kuro Tools (https://github.com/nnguyen259/KuroTools/releases) to prepare json.
# GitHub eArmada8/misc_kiseki

items = {}
with open("t_item.json", 'rb') as f:
    item_data_stream = f.read()

data_start = item_data_stream.find(b'"data":')
item_table_start = item_data_stream.find(b'"name": "ItemTableData",', data_start)
item_table_end = item_data_stream.find(b'"name": "ItemKindParam2",', item_table_start)
item_table_stream = item_data_stream[item_table_start:item_table_end]
current_offset = item_table_start
while current_offset > 0:
    id_offset = item_table_stream.find(b'\x0d\x0a\x09\x09\x09\x09\x09\x22\x69\x64\x22\x3a\x20', current_offset) + 13 # Jump to item ID
    if id_offset < 13: #no further items
        break
    id = item_table_stream[id_offset:item_table_stream.find(b'\x2c',id_offset)]
    name_offset = item_table_stream.find(b'\x0d\x0a\x09\x09\x09\x09\x09\x22\x6e\x61\x6d\x65\x22\x3a\x20',id_offset) + 15
    name  = item_table_stream[name_offset+1:item_table_stream.find(b'\x22\x2c',name_offset)]
    items[id] = name
    current_offset = name_offset

sorted_items = dict(sorted(items.items(), key=lambda item: ''.join(filter(str.isalnum,item[1].decode()))))

with open('item_table.csv', 'wb') as f:
    for key in sorted_items.keys():
        f.write(key+b',"'+str(items[key],'utf-8').replace('"','\\"').encode('utf8')+'"\r\n'.encode('utf8'))

with open('item_table_for_CE_lua.txt', 'wb') as f:
    for key in sorted_items.keys():
        f.write(b'"'+key+b':'+str(items[key],'utf-8').replace('"','\\"').encode('utf8')+'",\r\n'.encode('utf8'))