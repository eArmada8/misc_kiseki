# misc_kiseki
Random code for Kiseki (trails) modding

This is a storage space for miscellaneous scripts I've written for trails of cold steel 3 / 4 / hajimari no kiseki modding.  Currently:

aa - decompresspkg.py:  This script decompresses files inside .pkg files, resulting in a bigger (but more compatible) .pkg file.  Needed if you want to use CLE Hajimari assets in NISA CS3/CS4.

aa - inject model.py:  This script is used for model swapping.  Place in the asset folder and execute.  It will first ask for the (source) model you want to inject, and then the (target) model you want replaced.  It will make a backup copy of the target model (with .original filename) if no backup already exists, and then replace the target model package with the source model package.  Also, if a backup copy of the source model exists, then it will use the backup and not the current package.  This is so you can do swaps - if you instruct it to replace A with B and then B with A, it will swap them.  (Assuming no changes have yet been made, in the first injection it will use A, backup B, and replace B with A.  Then in the second inject, it will use *the backup of B*, backup A, and thus replace A with B.)  Tested with NISA CS3, NISA CS4, CLE Hajimari.

name_table_decode.py:  Take the t_name.tbl and decode it into a readable spreadsheet (saved in the same directory as table.csv).  Put it in the folder {trails game}/data/text/dat_en and execute.  Tested with ToCS3 (NISA), ToCS4 (NISA), Hajimari no Kiseki CLE fan trans, file is in /data/text/dat instead).
