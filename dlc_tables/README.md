# Trails of Cold Steel III / IV / into Reverie DLC table maker for custom costumes.

This is a small script to write t_attach.tbl, t_dlc.tbl and t_item.tbl for making costume mods in Trails of Cold Steel III, IV and into Reverie NIS America releases for PC (DirectX 11).  Other platforms / CLE releases are not tested, so YMMV.

## Credits

This tool uses the .csv output for t_name.tbl from the [tbled editor](https://git.sr.ht/~quf/tocs/tree/trunk/tbled/README.md) by Lukas Himbert.  I also want to thank My Name for teaching me how to make the tables and helping me troubleshoot the table-making process, and Ouroboros for the Falcom Decompiler.

## Requirements:
1. Python 3.9 or newer is required for use of this script.  It is free from the Microsoft Store, for Windows users.  For Linux users, please consult your distro.

## How to use

### make_dlc_tbls.py

*This script expects 3 tables, ed83nisa.csv, ed84nisa.csv and ed85nisa.csv for CS3, CS4 and Reverie.  (You only need the table for the games you are modding.)  They come with the release archive of this tool, but if you are downloading this tool from GitHub, you can generate them yourself.  Download the [tbled editor](https://git.sr.ht/~quf/tocs/tree/trunk/tbled/README.md) by Lukas Himbert.  Use it to open t_name.tbl from each game (located at* `{cold steel}/data/text/data` *or* `{cold steel}/data/text/data_en)` *then export to csv with the filename above.*

Before you start, you will want to determine some information:
1. DLC ID number:  This will be the same as the folder number in `{CS4/Reverie}/data/dlc/text/xxxx` where xxxx is the 4 digit number of the folder.  I recommend keeping the number <200, but be sure to use a number that isn't already in use.
2. Item ID numbers:  You need to choose item numbers that are valid, but are not already in the game.

You can use dlc_id_checker.py and item_id_checker.py to check for unused ID numbers.  Place the scripts inside your Trails of Cold Steel III/IV/Reverie folder (the root folder with the bin and data folders in it).  Run the scripts and it will tell you roughly what numbers are in use.  The easiest is to pick something slightly above the upper number, but do not go too high or the game will not accept the numbers.

Place all your .pkg files in a folder, and put make_dlc_tbls.py and csv files in the same folder.  Run make_dlc_tbls.py.  If there are .json files with settings, the script will just make the .tbl files, but the first time you run it (assuming you did not make the .json files by hand) it will ask you questions.

Questions it will ask you:
* DLC options:
	1. Game type:  Enter 3, 4 or 5 for CS3, CS4 or NISA Reverie.
	2. DLC ID:  This number should match the number of the folder in `{Base Folder}/data/dlc/text/xxxx` where xxxx is a 4 digit number folder that you are making.  Add leading zeros to the folder name to make 4 digits; e.g. if you chose 200 as your DLC ID, name the folder 0200.
	3. DLC Name:  The name of the DLC that the user will see in the DLC menu
	4. DLC Description:  The description of the DLC that the user will see in the DLC menu
* Item options:
	1. Item ID: This number should be unique and not already used by the game.  For attachments, if you want to group two or more attachments together (for example halo and angel wings), give them the same ID number.  The script will copy over the remaining information, except the attach point.
	2. Item Type: Enter 193 for costume, 194 for attachment, 195 for hair color or 454 for ARCUS cover.  Other types are not currently supported.
	3. Attach point: This field only appears for attachments.  The attach point should be in the .inf file for the costumes it supports.  Some example attach points include head_point, R_hand_point, DLC_point1, etc.
	4. Character ID: Please look in the t_name.tbl CSV files provided, or choose from the list the script gives you.  The script will look for any costume files in the folder and give those characters as options, but you can choose any ID under 200.  For example, Rean is 0, Alisa is 1, and so on.  Please note that this number is NOT the same as the C_CHRxxx number.  (For example, Juna's character ID is 10, even though her model is C_CHR011.  Please look in the CSV.)
	5. Item Name:  The name of the item that the user will see in the item / costume menus
	6. Item Description:  The description of the item that the user will see in the item / costume menus

Once you have answered all the questions, it will generate the 3 table files.  It will also generate a dlc.json file saving all the DLC options, and a .json file for each .pkg.  Running the script again, the tables will be generated without any questions.  If you want to change any of the data, edit the .json with a text editor, or simply delete the .json file.  If you just delete the file you want to change, the script will still use the other .json files it finds.

### dlc_conflict_resolver.py

Place the scripts inside your Trails of Cold Steel III/IV/Reverie folder (the root folder with the bin and data folders in it).  Run the script and it will tell you if there are multiple DLC tables using the same DLC numbers or the same item numbers in use.  When it finds two items using the same number, it will ask you which item you would like to reassign to a new number.  Be sure to pick the DLC you just installed; *do not renumber official Falcom items!*

For DLC, it will not let you renumber DLC IDs that match the folder name.  This can lead to impossible situations - for example, if you number your DLC 95 and put it in folder `/data/dlc/text/0095` but it conflicts with an official Falcom 95, my script will not let you renumber the conflicting DLC *(and I highly discourage renumbering the official Falcom DLC)*.  In this case, rename the folder `/data/dlc/text/1195` or something else equally invalid, and the script will let you renumber the DLC.  Copy down the new number, and rename the folder to match.  For example, if you rename `/data/dlc/text/0095` to `/data/dlc/text/1195` and then the script changes the number from 95 to 180, then subsequently rename `/data/dlc/text/1195` to `/data/dlc/text/0180`.

This script will attempt to silently repair corrupt table pointers.

### make_dlc_jsons_from_tbls.py

Place in a folder with t_attach.tbl, t_item.tbl and t_dlc.tbl (all three should have been previously generated by this toolset; there is no guarantee it will work if the tables were generated with a different tool).  Run the script, and it will extract all the metadata into .json files that can be used with make_dlc_tbls.py.

### add_items_to_t_shop.py

This script will add DLC items to a shop, so that they can be purchased.

- Obtain `t_shop.tbl` from the game text dat folder, generally `{Base Folder}/data/text/dat_en` or `{Base Folder}/data/text/dat`.
- Put a copy of the original `t_shop.tbl` in a folder with this script, name it `t_shop.tbl.original`.  The script will never overwrite `t_shop.tbl.original`, but will write a new `t_shop.tbl` instead.
- Make a folder with the shop_id number.  For example, 1041 is the reverie corridor costume shop, so make a `1041` folder.
- Inside the folder, put json files generated by make_dlc_tbls.py.  The script will read the item_id numbers from the jsons and add each one to the shop.
- Run add_items_to_t_shop.py and it will write a brand new `t_shop.tbl`.
- Place the new `t_shop.tbl` in the game text dat folder, overwriting the original.

It will always start with `t_shop.tbl.original`, so you can run it over and over and not worry about duplicate entries.  You can add as many items to as many shops as you want; just make a folder for each shop.