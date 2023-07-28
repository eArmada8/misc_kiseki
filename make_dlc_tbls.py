# Short script to generate a set of dlc tables for custom costumes in Trails of Cold Steel IV
# GitHub eArmada8/misc_kiseki

import os, csv, json, struct, glob

class dlc_table_maker:
    def __init__ (self):
        self.dlc_details = self.get_dlc_details()
        self.name_dict = self.get_names({4:'ed84nisa.csv', 5:'ed85nisa.csv'}[self.dlc_details['game_type']])
        self.packages = self.get_pkg_details()
        self.package_list = list(self.packages.keys())

    def get_dlc_details (self):
        if os.path.exists('dlc.json'):
            with open('dlc.json', 'r') as f:
                dlc_details = json.loads(f.read())
        else:
            dlc_details = {}
        while 'game_type' not in dlc_details.keys() or dlc_details['game_type'] not in [4,5]:
            item_type_raw = input("Which game? [4=CS4, 5=NISA Reverie, leave blank for 4] ")
            if item_type_raw == '':
                dlc_details['game_type'] = 4
            else:
                try:
                    dlc_details['game_type'] = int(item_type_raw)
                    if dlc_details['game_type'] not in [4,5]:
                        print("Invalid entry!")
                except ValueError:
                    print("Invalid entry!")
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

    #Takes NameTableData.csv from tbled
    def get_names (self, tablename = 'ed84nisa.csv'):
        import csv
        name_dict = {}
        with open(tablename, encoding='utf-8') as csvfile:
            names = csv.reader(csvfile, delimiter=',')
            for row in names:
                #if not row[0] == 'character' and not row[0] == '65535':
                if not row[0] == 'character' and int(row[0]) < 200 and len(row[2].split("_")) == 2:
                    if row[2] not in name_dict.keys():
                        name_dict[row[2]] = {'chr_id': int(row[0]), 'chr_name': row[1]}
        return(name_dict)

    def get_items_from_jsons (self):
        items = {}
        jsons = glob.glob('*.pkg.json')
        for i in range(len(jsons)):
            with open(jsons[i], 'r') as f:
                pkg_details = json.loads(f.read())
            if 'item_id' in pkg_details.keys():
                items[pkg_details['item_id']] = pkg_details
        return(items)

    def get_chr_id (self, pkg_name):
        try:
            return(self.name_dict["_".join(pkg_name.split("_")[0:2])]['chr_id'])
        except KeyError:
            return 0x1FFFFFFF # This number is meaningless, just used to catch errors

    def get_chr_name (self, chr_id):
        try:
            return([x['chr_name'] for x in self.name_dict.values() if x['chr_id'] == chr_id][0])
        except KeyError:
            return ''

    def get_pkg_details (self):
        packages = glob.glob('*.pkg')
        unique_chars = list(set([self.get_chr_id(x) for x in packages if self.get_chr_id(x) != 0x1FFFFFFF]))
        existing_items = self.get_items_from_jsons()
        pkg_dict = {}
        for i in range(len(packages)):
            if os.path.exists(packages[i] + '.json'):
                with open(packages[i] + '.json', 'r') as f:
                    pkg_details = json.loads(f.read())
            else:
                pkg_details = {}
            while 'item_id' not in pkg_details.keys():
                print("Note: If you want two attachments to be grouped, give them the same item ID.")
                item_id_raw = input("Item ID number for {0}: ".format(packages[i]))
                try:
                    pkg_details['item_id'] = int(item_id_raw)
                    if pkg_details['item_id'] in list(existing_items.keys()):
                        pkg_details['item_type'] = existing_items[pkg_details['item_id']]['item_type']
                        pkg_details['chr_id'] = existing_items[pkg_details['item_id']]['chr_id']
                        pkg_details['item_name'] = existing_items[pkg_details['item_id']]['item_name']
                        pkg_details['item_desc'] = existing_items[pkg_details['item_id']]['item_desc']
                except ValueError:
                    print("Invalid entry!")
            while 'item_type' not in pkg_details.keys() or pkg_details['item_type'] not in [193,194,195]:
                item_type_raw = input("Item type for {0}: [193=costume, 194=attachment, 195=hair color, leave blank for 193] ".format(packages[i]))
                if item_type_raw == '':
                    pkg_details['item_type'] = 193
                else:
                    try:
                        pkg_details['item_type'] = int(item_type_raw)
                        if pkg_details['item_type'] not in [193,194,195]:
                            print("Invalid entry!")
                    except ValueError:
                        print("Invalid entry!")
            while 'attach_point' not in pkg_details.keys() or pkg_details['attach_point'] == '':
                if pkg_details['item_type'] == 194:
                    pkg_details['attach_point'] = str(input("Attach point for {0}: (e.g. head_point - check .inf file for valid options)  ".format(packages[i]))).encode('utf-8').decode('utf-8')
                else:
                    pkg_details['attach_point'] = 'null'
            while 'chr_id' not in pkg_details.keys() or pkg_details['chr_id'] == 0x1FFFFFFF:
                pkg_details['chr_id'] = self.get_chr_id(packages[i])
                if pkg_details['chr_id'] == 0x1FFFFFFF: #Non-costume
                    print("Please choose a character for {0}: ".format(packages[i]))
                    print("-1. Any character")
                    for j in range(len(unique_chars)):
                        print("{0}. {1}".format(unique_chars[j], self.get_chr_name(unique_chars[j])))
                    print("(Any number <200 is accepted, see {0} for other options)".format({4:'ed84nisa.csv', 5:'ed85nisa.csv'}[self.dlc_details['game_type']]))
                    chr_id_raw = input("Character restriction for {0}: ".format(packages[i]))
                    try:
                        if int(chr_id_raw) == -1:
                            pkg_details['chr_id'] = 0xFFFF
                        else:
                            if int(chr_id_raw) < 200:
                                pkg_details['chr_id'] = int(chr_id_raw)
                            else:
                                print("Invalid entry!")
                    except ValueError:
                        print("Invalid entry!")
            while 'item_name' not in pkg_details.keys() or pkg_details['item_name'] == '':
                pkg_details['item_name'] = str(input("Item Name for {0}: ".format(packages[i]))).encode('utf-8').decode('utf-8')
            while 'item_desc' not in pkg_details.keys() or pkg_details['item_desc'] == '':
                pkg_details['item_desc'] = str(input("Item Description for {0}: ".format(packages[i]))).encode('utf-8').decode('utf-8')
            pkg_dict[packages[i]] = pkg_details
            if pkg_details['item_id'] not in list(existing_items.keys()):
                existing_items[pkg_details['item_id']] = pkg_details
            with open(packages[i] + '.json', "wb") as f:
                f.write(json.dumps(pkg_details, indent=4).encode("utf-8"))
        return(pkg_dict)
        
    #The second number isn't always 1, but for small tables this should be ok
    def make_tbl_header (self, item_count, name):
        return(struct.pack("<hi", item_count, 1) + name.encode() + b'\x00' + struct.pack("<i", item_count))

    def make_item_entry (self, pkg_name):
        item_tbl_entry = struct.pack("<5h", self.packages[pkg_name]['item_id'], self.packages[pkg_name]['chr_id'],\
            48, 0, self.packages[pkg_name]['item_type'])
        if self.dlc_details['game_type'] == 5: #NISA Reverie
            item_tbl_entry += struct.pack("<64hb", *[0]*65)
            # The first two numbers are constant and same as CS4, the second two seem random, maybe sorting or a timestamp?
            item_tbl_entry += struct.pack("<4h", 99, 0, 12021, 32)
        else: #Defaults to Cold Steel IV
            item_tbl_entry += struct.pack("<70h", *[0]*70)
            item_tbl_entry += struct.pack("<3h", 99, 5005, self.dlc_details['dlc_id'])
        item_tbl_entry += self.packages[pkg_name]['item_name'].encode('utf-8') + b'\x00'
        item_tbl_entry += self.packages[pkg_name]['item_desc'].encode('utf-8') + b'\x00'
        if self.dlc_details['game_type'] == 5: #NISA Reverie
            pass
        else: #Defaults to Cold Steel IV
            item_tbl_entry += struct.pack("<2i", 0, 0)
        return(b'item\x00' + struct.pack("<h",len(item_tbl_entry)) + item_tbl_entry)

    def make_attach_entry (self, pkg_name):
        attach_tbl_entry = struct.pack("<3hi", self.packages[pkg_name]['chr_id'],\
            {193:5, 194:67, 195: 9}[self.packages[pkg_name]['item_type']], 0, self.packages[pkg_name]['item_id'])
        attach_tbl_entry += struct.pack("<4ih", 0, 0, 0, -1, 48)
        attach_tbl_entry += pkg_name.split('.')[0].encode() + b'\x00' #Split is to remove the .pkg
        attach_tbl_entry += self.packages[pkg_name]['attach_point'].encode() + b'\x00'
        return(b'AttachTableData\x00' + struct.pack("<h",len(attach_tbl_entry)) + attach_tbl_entry)

    def make_dlc_entry (self):
        dlc_tbl_entry = struct.pack("<2h", self.dlc_details['dlc_id'], 5008) # I think the second number has something to do with sorting?
        dlc_tbl_entry += struct.pack("<8h", *[0]*8)
        dlc_tbl_entry += self.dlc_details['dlc_name'].encode('utf-8') + b'\x00'
        dlc_tbl_entry += self.dlc_details['dlc_desc'].encode('utf-8') + b'\x00'
        items_added = []
        for i in range(len(self.package_list)):
            if self.packages[self.package_list[i]]['item_id'] not in items_added:
                dlc_tbl_entry += struct.pack("<2h", self.packages[self.package_list[i]]['item_id'], 1) # Second number is quantity
                items_added.append(self.packages[self.package_list[i]]['item_id'])
        if 20 - len(items_added) > 0:
            for i in range(20 - len(items_added)):
                dlc_tbl_entry += struct.pack("<2h", 9999, 0)
        return(b'dlc\x00' + struct.pack("<h",len(dlc_tbl_entry)) + dlc_tbl_entry)

    def make_item_tbl (self, write_table = True):
        items_added = []
        item_tbl = bytes()
        for i in range(len(self.package_list)):
            if self.packages[self.package_list[i]]['item_id'] not in items_added:
                item_tbl += self.make_item_entry(self.package_list[i])
                items_added.append(self.packages[self.package_list[i]]['item_id'])
        item_tbl = self.make_tbl_header(len(items_added), 'item') + item_tbl
        if write_table == True:
            with open("t_item.tbl","wb") as f:
                f.write(item_tbl)
        return(item_tbl)

    def make_attach_tbl (self, write_table = True):
        attach_tbl = self.make_tbl_header(len(self.package_list), 'AttachTableData')
        for i in range(len(self.package_list)):
            attach_tbl += self.make_attach_entry(self.package_list[i])
        if write_table == True:
            with open("t_attach.tbl","wb") as f:
                f.write(attach_tbl)
        return(attach_tbl)

    def make_dlc_tbl (self, write_table = True):
        dlc_tbl = self.make_tbl_header(1, 'dlc')
        dlc_tbl += self.make_dlc_entry() # I think we can put more than one entry
        if write_table == True:
            with open("t_dlc.tbl","wb") as f:
                f.write(dlc_tbl)
        return(dlc_tbl)

if __name__ == "__main__":
    global name_dict
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    dlc_table_maker = dlc_table_maker()
    dlc_table_maker.make_item_tbl()
    dlc_table_maker.make_attach_tbl()
    dlc_table_maker.make_dlc_tbl()
