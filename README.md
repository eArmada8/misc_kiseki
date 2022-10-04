# misc_kiseki
Random code for Kiseki (trails) modding

This is a storage space for miscellaneous scripts I've written for Falcom games (Kiseki / Trails etc) modding.  Currently:

3dmigoto_mod_picker.py:  This script recursively searches a 3DMigoto Mods directory and looks for multiple calls to duplicate hashes.  It disables directories (based on user choice) so that only one directory is enabled for each cluster of identical hashes (128-bit).  256-bit hashes (shaders) all get rewritten to allow duplicate calls.

a00000 - inject kuro model.py:  Same as "aa - inject model.py" but for Kuro no Kiseki CLE

aa - decompresspkg.py:  This script decompresses files inside .pkg files, resulting in a bigger (but more compatible) .pkg file.  Needed if you want to use CLE Hajimari assets in NISA CS3/CS4.

aa - inject model.py:  This script is used for model swapping.  Place in the asset folder and execute.  It will first ask for the (source) model you want to inject, and then the (target) model you want replaced.  It will make a backup copy of the target model (with .original filename) if no backup already exists, and then replace the target model package with the source model package.  Also, if a backup copy of the source model exists, then it will use the backup and not the current package.  This is so you can do swaps - if you instruct it to replace A with B and then B with A, it will swap them.  (Assuming no changes have yet been made, in the first injection it will use A, backup B, and replace B with A.  Then in the second inject, it will use *the backup of B*, backup A, and thus replace A with B.)  Tested with NISA CS1, CS2, CS3, NISA CS4, CLE Hajimari, Tokyo Xanadu eX+ (although use dedicated version for TXe instead).  Requires my fork of unpackpkg.py (eArmada/unpackpkg).

aa - txe inject model.py:  Same as "aa - inject model.py" but for Tokyo Xanadu eX+.  Automatically pulls the required files from the .bra archives for injection.  Requires txe_file_extract.py and my fork of unpackpkg.py (eArmada/unpackpkg).

item_table_decode.py:  Meant to extract names and ID numbers from t_item.tbl so that they can be used in a cheat engine table.

kuro_item_json_to_table.py:  Same as "item_table_decode.py" but for Kuro no Kiseki CLE; requires KuroTools JSON output (https://github.com/nnguyen259/KuroTools)

name_table_decode.py:  Take the t_name.tbl and decode it into a readable spreadsheet (saved in the same directory as table.csv).  Put it in the folder {trails game}/data/text/dat_en and execute.  Tested with ToCS3 (NISA), ToCS4 (NISA), Hajimari no Kiseki CLE fan trans, file is in /data/text/dat instead).

txe_file_extract.py:  Searches .bra files in the current directory and extracts files.  Will preserve directory structure.
