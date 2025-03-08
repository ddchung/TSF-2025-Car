# dataset splitter

from cProfile import label
import os
import glob

DATASET_DIR = "traffic_sign_frames"

if not os.path.exists(os.path.join(DATASET_DIR, "train")):
    os.makedirs(os.path.join(DATASET_DIR, "train"))

if not os.path.exists(os.path.join(DATASET_DIR, "val")):
    os.makedirs(os.path.join(DATASET_DIR, "val"))


images = glob.glob(os.path.join(DATASET_DIR, "*.jpg"))

print(f"Found {len(images)} images")

train_images = images[:int(len(images) * 0.8)]
val_images = images[int(len(images) * 0.8):]

for image in train_images:
    label_file = image.replace(".jpg", ".xml")
    print("image", image, "label", label_file)
    if not os.path.exists(label_file):
        continue
    os.rename(label_file, os.path.join(DATASET_DIR, "train", os.path.basename(label_file)))
    os.rename(image, os.path.join(DATASET_DIR, "train", os.path.basename(image)))

for image in val_images:
    label_file = image.replace(".jpg", ".xml")
    print("image", image, "label", label_file)
    if not os.path.exists(label_file):
        continue
    os.rename(label_file, os.path.join(DATASET_DIR, "val", os.path.basename(label_file)))
    os.rename(image, os.path.join(DATASET_DIR, "val", os.path.basename(image)))
