# lane navigation data reviewer

import cv2
import os
import glob
import steering_line

IN_DIR = 'lane_nav_data'

files = glob.glob(IN_DIR + '/*.jpg')

ok_files = []
ng_files = []

def get_angle(file):
    return int(file.split('_')[-2])

for i, file in enumerate(files):
    img = cv2.imread(file)
    angle = get_angle(file) - 90
    img = steering_line.draw_steering_curve(img, angle)
    cv2.imshow('image', img)
    ok = False
    while not ok:
        key = cv2.waitKey(0)
        if key == ord('q'):
            exit()
        elif key == ord('y'):
            ok = True
            break
        elif key == ord('n'):
            ok = False
            break
    if ok:
        print(f'{i+1}/{len(files)}: {file} -> OK')
        ok_files.append(file)
    else:
        print(f'{i+1}/{len(files)}: {file} -> NG')
        ng_files.append(file)

print('\033[1;32mOK files:\033[0m')
print(ok_files)
print('\033[1;31mNG files:\033[0m')
print(ng_files)

should_delete = input('Delete NG files? (y/n): ')
if should_delete == 'y':
    for file in ng_files:
        os.remove(file)
        print(f'{file} deleted')
    print('NG files deleted')
else:
    print('NG files not deleted')    

cv2.destroyAllWindows()

