# Short script / library to extract files from BRA archives in Tokyo Xanadu eX+.  It can be used in interactive
# mode, with command line arguments, or as a library.  Thanks to Sewer56, Luigi Auriemma (QuickBMS), Ekey@Xentax!
# Instructions: /path/to/python3 txe_file_extract.py --help
# GitHub eArmada8/misc_kiseki

import os, struct, sys, glob, zlib

def get_archivelist():
    return glob.glob('*.bra')

def get_filelist(archivefile):
    if os.path.exists(archivefile):
        with open(archivefile, 'rb') as f:
            fileHeader = f.read(4)
            if fileHeader != b'PDA\x00':
                return(False)
            compressionType, = struct.unpack('<I', f.read(4))
            fileEntryOffset, = struct.unpack('<I', f.read(4))
            fileCount, = struct.unpack('<I', f.read(4))
            fileList = []
            f.seek(fileEntryOffset)
            for i in range(fileCount):
                fileEntry = {}
                fileEntry["fileNameOffset"] = f.tell()
                fileEntry["filePackedTime"], = struct.unpack('<I', f.read(4))
                fileEntry["unknown"], = struct.unpack('<I', f.read(4))
                fileEntry["compressedSize"], = struct.unpack('<I', f.read(4))
                fileEntry["uncompressedSize"], = struct.unpack('<I', f.read(4))
                fileEntry["fileNameLength"], = struct.unpack('<H', f.read(2))
                fileEntry["fileFlags"], = struct.unpack('<H', f.read(2))
                fileEntry["fileOffset"], = struct.unpack('<I', f.read(4))
                # decode / encode is to sanitize name by removing all non-ASCII characters
                fileEntry["fileNameEntry"] = f.read(fileEntry["fileNameLength"]).decode('ascii','ignore').encode()
                if (fileEntry["fileNameEntry"].find(b'\x00') >= 0):
                    fileEntry["fileNameEntry"] = fileEntry["fileNameEntry"][:fileEntry["fileNameEntry"].find(b'\x00')]
                fileEntry["fileName"] = fileEntry["fileNameEntry"][fileEntry["fileNameEntry"].rfind(b'\\')+1:]
                if (fileEntry["fileNameEntry"].rfind(b'\\') >= 0):
                    fileEntry["dirName"] = fileEntry["fileNameEntry"][:fileEntry["fileNameEntry"].rfind(b'\\')]
                else:
                    fileEntry["dirName"] = ''
                fileEntry["archiveName"] = archivefile
                fileList.append(fileEntry)
        return(fileList)
    else:
        return(False)

def filter_filelist(fileList, fileName, exact_match = True):
    if exact_match == True:
        return list(filter(lambda file: fileName.lower().encode() == file["fileName"].lower(), fileList))
    else:
        return list(filter(lambda file: fileName.lower().encode() in file["fileName"].lower(), fileList))

def find_file(fileName, exact_match = True, specific_archive = False):
    archives = get_archivelist()
    if (specific_archive != False):
        archives = list(filter(lambda archive: specific_archive.lower() in archive.lower(), archives))
    files = []
    for i in range(len(archives)):
        files.extend(filter_filelist(get_filelist(archives[i]), fileName, exact_match))
    return(files)

def extract_filedata(fileEntry):
    with open(fileEntry["archiveName"], 'rb') as f:
        f.seek(fileEntry['fileOffset'] + 16)
        if fileEntry['uncompressedSize'] <= fileEntry['compressedSize']:
            return(f.read(fileEntry['uncompressedSize'] - 16))
        else:
            return(zlib.decompress(f.read(fileEntry['compressedSize'] - 16), wbits=-15))

def extract_single_file(fileEntry, overwrite = False, interactive = False):
    filedata = extract_filedata(fileEntry)
    basedir = os.path.abspath(os.getcwd())
    result = 0
    if not fileEntry['dirName'] == '':
        filedir = fileEntry['dirName'].decode().split('\\')
        for j in range(len(filedir)):
            if not os.path.exists(filedir[j]): 
                os.mkdir(filedir[j])
            os.chdir(filedir[j])
    if os.path.exists(fileEntry['fileName'].decode()) and (interactive == True):
        if str(input(fileEntry['fileNameEntry'].decode() + " exists! Overwrite with version from " \
            + fileEntry['archiveName'] + "? (y/N) ")).lower()[0:1] == 'y':
            overwrite = True
    if (overwrite == True) or not os.path.exists(fileEntry['fileName'].decode()):
        with open(fileEntry['fileName'].decode(),'wb') as f_out:
            result = f_out.write(filedata)
        os.utime(fileEntry['fileName'].decode(), (fileEntry['filePackedTime'], fileEntry['filePackedTime']))
    os.chdir(basedir)
    return(result)

def extract_files(fileName, overwrite = False, exact_match = True, interactive = False, specific_archive = False):
    fileEntries = find_file(fileName, exact_match, specific_archive)
    for i in range(len(fileEntries)):
        extract_single_file(fileEntries[i], overwrite, interactive)

def extract_archive(archivename, overwrite = False, interactive = False):
    if os.path.exists(archivename):
        fileEntries = get_filelist(archivename)
        for i in range(len(fileEntries)):
            extract_single_file(fileEntries[i], overwrite, interactive)
        return(True)
    else:
        return(False)

if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    # Grab filename and options from command line arguments, if invoked from commandline
    if len(sys.argv) > 1:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('-e', '--exact', help="Search for exact match only", action="store_true")
        parser.add_argument('-o', '--overwrite', help="Overwrite existing files", action="store_true")
        parser.add_argument('-a', '--archive', help="Search only in this archive (e.g. --archive System.bra)", nargs=1, default=False)
        parser.add_argument('filename', help="Name of file(s) to extract.  " \
            + "If a .bra file then will extract entire archive, otherwise will search all .bra files for this file.")
        args = parser.parse_args()
        if args.filename[-4:] == '.bra':
            extract_archive(args.filename, overwrite = args.overwrite, interactive = False)
        else:
            extract_files(args.filename, overwrite = args.overwrite, exact_match = args.exact, \
                interactive = False, specific_archive = args.archive[0])
    else:
        fileName = str(input("Please enter the name of files to extract: [partial matches allowed]  "))
        if fileName[-4:] == '.bra':
            extract_archive(fileName, overwrite = False, interactive = True)
        else:
            extract_files(fileName, overwrite = False, exact_match = False, interactive = True)
