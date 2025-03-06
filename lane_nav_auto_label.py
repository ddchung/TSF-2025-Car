# automatic labelling

import glob
import os

files = glob.glob("/Users/tin/Desktop/AiLabel/*.mov")

for file in files:
    open_bracket = "{"
    close_bracket = "}"
    cmd = f"( deactivate || true ) && cd /Users/tin/TSF-2025-Car/ && source bin/activate && python test2.py \'{file}\' &"

    print(cmd)
    # fork
    os.system(cmd)
