# A small script to insert loop data (inputted as MM:SS.SSS minutes seconds milliseconds)
# into .opus music files for use in Trails of Cold Steel III/IV and Trails into Reverie.
# Place insert_loop_metadata_into_opus.py in the same folder as the .opus file and double-click.
# Edit the header with the path to ffmpeg.exe prior to usage.
# 
# GitHub eArmada8/misc_kiseki

import glob, sys, os

# Should be 48000 for CS3/CS4/Reverie
sample_rate = 48000

# Edit the following line to point to ffmpeg.exe
path_to_ffmpeg = '/path/to/ffmpeg.exe'

if __name__ == '__main__':
    # Set current directory
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    else:
        os.chdir(os.path.abspath(os.path.dirname(__file__)))

    raw_filename = input("Filename: ")
    filenames = glob.glob(raw_filename) # Verify the file actually exists, and pass the absolute path to ffmpeg
    if len(filenames) > 0:
        # input the start of the loop, and convert from timestamp to frame number
        raw_start = input("Loop start in MM:SS.SSS: ")
        start_time = [int(x) if x.isnumeric() else 0 for x in raw_start.replace(':','.').split('.')]
        while len(start_time) < 3:
            start_time = [0]+start_time
        loop_start = round((start_time[0] * 60 + start_time[1] + start_time[2] / 1000.0) * sample_rate)
        # input the end of the loop, and convert from timestamp to frame number
        raw_end = input("Loop end in MM:SS.SSS: ")
        end_time = [int(x) if x.isnumeric() else 0 for x in raw_end.replace(':','.').split('.')]
        while len(end_time) < 3:
            end_time = [0]+end_time
        loop_end = round((end_time[0] * 60 + end_time[1] + end_time[2] / 1000.0) * sample_rate)
        # Run ffmpeg
        os.system('{0} -i "{1}" -metadata loopstart={2} -metadata loopend={3} -metadata loops={2}-{3} -codec copy "{4}"'.format(path_to_ffmpeg,\
            filenames[0], loop_start, loop_end, '_new.'.join(filenames[0].split('.'))))