# A script to move meshes in 3D space using values defined in a .json file.
# An alternative to AttachTransformData for games such as CS3 that do not have
# the option to systematically move meshes for different characters (for example
# moving earrings to account for varying head size).
#
# Requires numpy, which can be installed by:
# /path/to/python3 -m pip install numpy
#
# Requires lib_fmtibvb.py, place in the same folder.
#
# GitHub eArmada8/misc_kiseki

# If True, positive x shift will shift away from the center (magnitude shifting)
absolute_x = True

try:
    import shutil, numpy, os, sys, glob
    from lib_fmtibvb import *
except ModuleNotFoundError as e:
    print("Python module missing! {}".format(e.msg))
    input("Press Enter to abort.")
    raise

def shift_pos (meshname, z = 0, y = 0, x = 0, scale = 1):
    global absolute_x
    fmt = read_fmt(meshname+'.fmt')
    vb = read_vb(meshname+'.vb',fmt)
    pos_buffer = numpy.array(vb[0]['Buffer'])
    if absolute_x:
        new_pos_buffer = [((val * scale) + [x, z, y]) if val[0] >= 0 \
            else ((val * scale) + [-x, z, y]) for val in pos_buffer]
    else:
        new_pos_buffer = [((val * scale) + [x, z, y]) for val in pos_buffer]
    vb[0]['Buffer'] = new_pos_buffer
    write_vb(vb,meshname+'.vb',fmt)
    return

def process_folder (folder = 'meshes', z = 0, y = 0, x = 0, scale = 1):
    if os.path.exists('meshes/'):
        # Create a backup if one does not already exist
        if not os.path.exists('meshes.original/'):
            os.mkdir('meshes.original')
            for file in glob.glob('meshes/*'):
                shutil.copy2(file, 'meshes.original/')
        # Empty current meshes folder, copy all files from the backup
        shutil.rmtree('meshes')
        os.mkdir('meshes')
        for file in glob.glob('meshes.original/*'):
            shutil.copy2(file, 'meshes/')
        for file in [x[:-4] for x in glob.glob('meshes/*.fmt')]:
            shift_pos(file, z, y, x, scale)

if __name__ == "__main__":
    # Set current directory
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    else:
        os.chdir(os.path.abspath(os.path.dirname(__file__)))
    # If argument given, attempt to export from file in argument
    if len(sys.argv) > 1:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('json_filename', help="Name of JSON file to read z and y from.")
        args = parser.parse_args()
        if os.path.exists(args.json_filename):
            values = read_struct_from_json(args.json_filename)
            process_folder('meshes',\
                values['z'] if 'z' in values else 0.0,\
                values['y'] if 'y' in values else 0.0,\
                values['x'] if 'x' in values else 0.0,\
                values['scale'] if 'scale' in values else 1.0)
    else:
        z,y = '',''
        while not isinstance(z, float):
            try:
                z = float(input("Z Shift: "))
            except ValueError:
                print("Invalid input!")
        while not isinstance(y, float):
            try:
                y = float(input("Y Shift: "))
            except ValueError:
                print("Invalid input!")
        while not isinstance(x, float):
            try:
                x = float(input("X Shift: "))
            except ValueError:
                print("Invalid input!")
        while not isinstance(scale, float):
            try:
                scale = float(input("Scale: "))
            except ValueError:
                print("Invalid input!")
        process_folder('meshes', z, y, x, scale)