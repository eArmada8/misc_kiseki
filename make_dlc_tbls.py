# Short script to generate a set of dlc tables for custom costumes in Trails of Cold Steel IV
# GitHub eArmada8/misc_kiseki

import os, csv, json, struct, glob

#Takes NameTableData.csv from tbled
def get_names (tablename = 'NameTableData.csv'):
    import csv
    name_list = {}
    with open(tablename, encoding='utf-8') as csvfile:
        names = csv.reader(csvfile, delimiter=',')
        for row in names:
            if not row[0] == 'character' and not row[0] == '65535':
                name_list[row[2]] = {'chr_id': int(row[0]), 'chr_name': row[1]}
    return(name_list)

name_dict = get_names()

def get_chr_id (pkg_name):
    global name_dict
    return(name_dict["_".join(pkg_name.split("_")[0:2])]['chr_id'])

def get_chr_name (pkg_name):
    global name_dict
    return(name_dict["_".join(pkg_name.split("_")[0:2])]['chr_name'])

def get_dlc_details ():
    if os.path.exists('dlc.json'):
        with open('dlc.json', 'r') as f:
            dlc_details = json.loads(f.read())
    else:
        dlc_details = {}
    while 'dlc_id' not in dlc_details.keys():
        dlc_id_raw = input("DLC ID number: ")
        try:
            dlc_details['dlc_id'] = int(dlc_id_raw)
        except ValueError:
            print("Invalid entry!")
    while 'dlc_name' not in dlc_details.keys() or dlc_details['dlc_name'] == '':
        dlc_details['dlc_name'] = str(input("DLC Name: ")).encode('utf-8').decode('utf-8')
    while 'dlc_desc' not in dlc_details.keys() or dlc_details['dlc_desc'] == '':
        dlc_details['dlc_desc'] = str(input("DLC Description: ")).encode('utf-8').decode('utf-8')
    with open('dlc.json', "wb") as f:
        f.write(json.dumps(dlc_details, indent=4).encode("utf-8"))
    return(dlc_details)

#The second number isn't always 1, but for small tables this should be ok
def make_tbl_header (item_count, name):
    return(struct.pack("<hi", item_count, 1) + name.encode() + b'\x00' + struct.pack("<i", item_count))

def make_item_entry (pkg_name, dlc_id):
    global name_dict
    if os.path.exists(pkg_name + '.json'):
        with open(pkg_name + '.json', 'r') as f:
            pkg_details = json.loads(f.read())
    else:
        pkg_details = {}
    while 'item_id' not in pkg_details.keys():
        item_id_raw = input("Item ID number for {0}: ".format(pkg_name))
        try:
            pkg_details['item_id'] = int(item_id_raw)
        except ValueError:
            print("Invalid entry!")
    while 'item_name' not in pkg_details.keys() or pkg_details['item_name'] == '':
        pkg_details['item_name'] = str(input("Item Name for {0}: ".format(pkg_name))).encode('utf-8').decode('utf-8')
    while 'item_desc' not in pkg_details.keys() or pkg_details['item_desc'] == '':
        pkg_details['item_desc'] = str(input("Item Description for {0}: ".format(pkg_name))).encode('utf-8').decode('utf-8')
    with open(pkg_name + '.json', "wb") as f:
        f.write(json.dumps(pkg_details, indent=4).encode("utf-8"))
    item_tbl_entry = struct.pack("<5h", pkg_details['item_id'], get_chr_id(pkg_name), 48, 0, 193)
    item_tbl_entry += struct.pack("<70h", *[0]*70)
    item_tbl_entry += struct.pack("<3h", 99, 5005, dlc_id)
    item_tbl_entry += pkg_details['item_name'].encode('utf-8') + b'\x00'
    item_tbl_entry += pkg_details['item_desc'].encode('utf-8') + b'\x00'
    item_tbl_entry += struct.pack("<2i", 0, 0)
    return(b'item\x00' + struct.pack("<h",len(item_tbl_entry)) + item_tbl_entry)

def make_attach_entry (pkg_name):
    #This function assumes the JSON already exists, unlike make_item_entry()
    with open(pkg_name + '.json', 'r') as f:
        pkg_details = json.loads(f.read())
    attach_tbl_entry = struct.pack("<3hi", get_chr_id(pkg_name), 5, 0, pkg_details['item_id'])
    attach_tbl_entry += struct.pack("<4ih", 0, 0, 0, -1, 48)
    attach_tbl_entry += pkg_name.split('.')[0].encode() + b'\x00' #Split is to remove the .pkg
    attach_tbl_entry += 'null'.encode() + b'\x00'
    return(b'AttachTableData\x00' + struct.pack("<h",len(attach_tbl_entry)) + attach_tbl_entry)

def make_dlc_entry (dlc_details):
    dlc_tbl_entry = struct.pack("<2h", dlc_details['dlc_id'], 5008) # I think the second number has something to do with sorting?
    dlc_tbl_entry += struct.pack("<8h", *[0]*8)
    dlc_tbl_entry += dlc_details['dlc_name'].encode('utf-8') + b'\x00'
    dlc_tbl_entry += dlc_details['dlc_desc'].encode('utf-8') + b'\x00'
    packages = glob.glob('*.pkg')
    for i in range(len(packages)):
        with open(packages[i] + '.json', 'r') as f:
            pkg_details = json.loads(f.read())
        dlc_tbl_entry += struct.pack("<2h", pkg_details['item_id'], 1) # Second number is quantity
    if 20 - len(packages) > 0:
        for i in range(20 - len(packages)):
            dlc_tbl_entry += struct.pack("<2h", 9999, 0)
    return(b'dlc\x00' + struct.pack("<h",len(dlc_tbl_entry)) + dlc_tbl_entry)

def make_item_tbl (dlc_details, write_table = True):
    packages = glob.glob('*.pkg')
    item_tbl = make_tbl_header(len(packages), 'item')
    for i in range(len(packages)):
        item_tbl += make_item_entry(packages[i], dlc_details['dlc_id'])
    if write_table == True:
        with open("t_item.tbl","wb") as f:
            f.write(item_tbl)
    return(item_tbl)

def make_attach_tbl (write_table = True):
    packages = glob.glob('*.pkg')
    attach_tbl = make_tbl_header(len(packages), 'AttachTableData')
    for i in range(len(packages)):
        attach_tbl += make_attach_entry(packages[i])
    if write_table == True:
        with open("t_attach.tbl","wb") as f:
            f.write(attach_tbl)
    return(attach_tbl)

def make_dlc_tbl (write_table = True):
    dlc_tbl = make_tbl_header(1, 'dlc')
    dlc_tbl += make_dlc_entry(dlc_details) # I think we can put more than one entry
    if write_table == True:
        with open("t_dlc.tbl","wb") as f:
            f.write(dlc_tbl)
    return(dlc_tbl)

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    dlc_details = get_dlc_details()
    make_item_tbl(dlc_details)
    make_attach_tbl()
    make_dlc_tbl()