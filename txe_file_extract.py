# Short script / library to extract files from BRA archives in Tokyo Xanadu eX+.  Thanks to Sewer56!
# GitHub eArmada8/misc_kiseki

import os, struct, sys, glob, re, shutil, zlib

def get_archivelist():
    return glob.glob('*.bra')

def get_filelist(archivefile):
    if os.path.exists(archivefile):
        with open(archivefile, 'rb') as f:
            fileHeader = f.read(4) #Should be PDA, could put error checking in at some point.
            compressionType, = struct.unpack('<I', f.read(4))
            fileEntryOffset, = struct.unpack('<I', f.read(4))
            fileCount, = struct.unpack('<I', f.read(4))
            fileList = []
            f.seek(fileEntryOffset)
            for i in range(fileCount):
                fileEntry = {}
                fileEntry["fileNameOffset"] = f.tell()
                fileEntry["filePackedTime"], = struct.unpack('<I', f.read(4))
                fileEntry["fileOtherTime"], = struct.unpack('<I', f.read(4))
                fileEntry["compressedSize"], = struct.unpack('<I', f.read(4))
                fileEntry["uncompressedSize"], = struct.unpack('<I', f.read(4))
                fileEntry["fileNameLength"], = struct.unpack('<H', f.read(2))
                fileEntry["fileFlags"], = struct.unpack('<H', f.read(2))
                fileEntry["fileOffset"], = struct.unpack('<I', f.read(4))
                fileEntry["fileNameEntry"] = f.read(fileEntry["fileNameLength"])
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

def find_file(fileName, exact_match = True):
    archives = get_archivelist()
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

def extract_file(fileName, overwrite = False, exact_match = True):
    fileEntries = find_file(fileName, exact_match)
    for i in range(len(fileEntries)):
        filedata = extract_filedata(fileEntries[i])
        basedir = os.path.abspath(os.getcwd())
        if not fileEntries[i]['dirName'] == '':
            filedir = fileEntries[i]['dirName'].decode().split('\\')
            for j in range(len(filedir)):
                if not os.path.exists(filedir[j]): 
                    os.mkdir(filedir[j])
                os.chdir(filedir[j])
        if (overwrite == True) or not os.path.exists(fileEntries[i]['fileName'].decode('utf8')):
            with open(fileEntries[i]['fileName'].decode('utf8'),'wb') as f_out:
                f_out.write(filedata)
        os.chdir(basedir)

if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    # Grab filename and options from command line arguments, if invoked from commandline
    if len(sys.argv) > 1:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('-e', '--exact', help="Search for exact match only", action="store_true")
        parser.add_argument('-o', '--overwrite', help="Overwrite existing files", action="store_true")
        parser.add_argument('filename', help="Name of file(s) to extract")
        args = parser.parse_args()
        fileName = args.filename
        extract_file(args.filename, overwrite = args.overwrite, exact_match = args.exact)
    else:
        fileName = str(input("Please enter the name of files to extract: [partial matches allowed]  "))
        extract_file(fileName, overwrite = False, exact_match = False)
