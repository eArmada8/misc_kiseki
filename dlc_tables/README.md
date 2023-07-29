# Trails of Cold Steel III / IV / into Reverie DLC table maker for custom costumes.

This is a small script to write t_attach.tbl, t_dlc.tbl and t_item.tbl for making costume mods in Trails of Cold Steel III, IV and into Reverie NIS America releases for PC (DirectX 11).  Other platforms / CLE releases are not tested, so YMMV.

## Credits

This tool uses the .csv output for t_name.tbl from the [tbled editor](https://git.sr.ht/~quf/tocs/tree/trunk/tbled/README.md) by Lukas Himbert.  I also want to thank My Name for teaching me how to make the tables and helping me troubleshoot the table-making process, and Ouroboros for the Falcom Decompiler.

## Requirements:
1. Python 3.9 or newer is required for use of this script.  It is free from the Microsoft Store, for Windows users.  For Linux users, please consult your distro.

## How to use

### This script expects 3 tables, ed83nisa.csv, ed84nisa.csv and ed85nisa.csv for CS3, CS4 and Reverie.  (You only need the table for the games you are modding.)  They come with the release archive of this tool, but if you are downloading this tool from GitHub, you can generate them yourself.  Download the [tbled editor](https://git.sr.ht/~quf/tocs/tree/trunk/tbled/README.md) by Lukas Himbert.  Use it to open t_name.tbl from each game (located at {cold steel}/data/text/data or {cold steel}/data/text/data_en) then export to csv with the filename above.

Before you start, you will want to determine some information:
1. DLC ID number:  This will be the same as the folder number in {CS4/Reverie}/data/dlc/text/xxxx where xxxx is the 4 digit number of the folder.  I recommend keeping the number <200, but be sure to use a number that isn't already in use.
2. Item ID numbers:  You need to choose item numbers that are valid, but are not already in the game.

You can use dlc_id_checker.py and item_id_checker.py to check for unused ID numbers.  Place the scripts inside your Trails of Cold Steel III/IV/Reverie folder (the root folder with the bin and data folders in it).  Run the scripts and it will tell you roughly what numbers are in use.  The easiest is to pick something slightly above the upper number, but do not go too high or the game will not accept the numbers.

Place all your .pkg files in a folder, and put make_dlc_tbls.py and csv files in the same folder.  Run make_dlc_tbls.py.  If there are .json files with settings, the script will just make the .tbl files, but the first time you run it (assuming you did not make the .json files by hand) it will ask you questions.

Questions it will ask you:
* DLC options:
	1. Game type:  Enter 3, 4 or 5 for CS3, CS4 or NISA Reverie.
	2. DLC ID:  This number should match the number of the folder in {Base Folder}/dlc/text/xxxx where xxxx is a 4 digit number folder that you are making.  Add leading zeros to the folder name to make 4 digits; e.g. if you chose 200 as your DLC ID, name the folder 0200.
	3. DLC Name:  The name of the DLC that the user will see in the DLC menu
	4. DLC Description:  The description of the DLC that the user will see in the DLC menu
* Item options:
	1. Item ID: This number should be unique and not already used by the game.  For attachments, if you want to group two or more attachments together (for example halo and angel wings), give them the same ID number.  The script will copy over the remaining information, except the attach point.
	2. Item Type: Enter 193 for costume, 194 for attachment or 195 for hair color.  Other types are not currently supported.
	3. Attach point: This field only appears for attachments.  The attach point should be in the .inf file for the costumes it supports.  Some example attach points include head_point, R_hand_point, DLC_point1, etc.
	4. Character ID: Please look in the t_name.tbl CSV files provided, or choose from the list the script gives you.  The script will look for any costume files in the folder and give those characters as options, but you can choose any ID under 200.  For example, Rean is 0, Alisa is 1, and so on.  Please note that this number is NOT the same as the C_CHRxxx number.  (For example, Juna's character ID is 10, even though her model is C_CHR011.  Please look in the CSV.)
	5. Item Name:  The name of the item that the user will see in the item / costume menus
	6. Item Description:  The description of the item that the user will see in the item / costume menus

Once you have answered all the questions, it will generate the 3 table files.  It will also generate a dlc.json file saving all the DLC options, and a .json file for each .pkg.  Running the script again, the tables will be generated without any questions.  If you want to change any of the data, edit the .json with a text editor, or simply delete the .json file.  If you just delete the file you want to change, the script will still use the other .json files it finds.