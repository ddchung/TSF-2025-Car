# Python script to relabel the images in a directory

import os
import shutil
import glob


IN_DIR = 'dataset'
OUT_DIR = 'lane_nav_data'

# input format: name_frame_angle.jpg
# output format: name_angle_frame.jpg
def cvt_name(name):
    name, frame, angle = name.split('_')
    angle = angle.split('.')[0]
    return name + '_' + angle + '_' + frame + '.jpg'



files = glob.glob(IN_DIR + '/*.jpg')
files.sort()

for i, file in enumerate(files):
    new_name = cvt_name(os.path.basename(file))
    shutil.copy(file, os.path.join(OUT_DIR, new_name))
    print(f'{i+1}/{len(files)}: {file} -> {new_name}')
