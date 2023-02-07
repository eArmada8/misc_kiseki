# misc_kiseki
Random code for Kiseki (trails) modding

This is a storage space for miscellaneous scripts I've written for Falcom games (Kiseki / Trails etc) modding.  Currently:

3dmigoto_mod_picker.py:  This script recursively searches a 3DMigoto Mods directory and looks for multiple calls to duplicate hashes.  It disables directories (based on user choice) so that only one directory is enabled for each cluster of identical hashes (128-bit).  256-bit hashes (shaders) all get rewritten to allow duplicate calls.


item_table_decode.py:  Meant to extract names and ID numbers from t_item.tbl so that they can be used in a cheat engine table.

kuro_item_json_to_table.py:  Same as "item_table_decode.py" but for Kuro no Kiseki CLE; requires KuroTools JSON output (https://github.com/nnguyen259/KuroTools)

name_table_decode.py:  Take the t_name.tbl and decode it into a readable spreadsheet (saved in the same directory as table.csv).  Put it in the folder {trails game}/data/text/dat_en and execute.  Tested with ToCS3 (NISA), ToCS4 (NISA), Hajimari no Kiseki CLE fan trans, file is in /data/text/dat instead).
