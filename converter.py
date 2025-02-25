import tensorflow as tf
from tensorflow import keras
import cv2
import glob

IMG_SIZE = (66, 200)
IMG_CHANNELS = 1

image_paths = glob.glob("lane_nav_data/*.jpg")

def dataset():
  for img in image_paths[:100]:
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # Read in grayscale
    img = cv2.resize(img, IMG_SIZE)  # Resize to model input size
    img = np.expand_dims(img, axis=-1)  # Add channel dimension (H, W, 1)
    img = np.expand_dims(img, axis=0)  # Add batch dimension (1, H, W, 1)
    img = img.astype(np.float32) / 255.0  # Normalize (if needed)
    yield [img]

model = keras.models.load_model("lane_navigation.keras", compile=False)
model.export("test")

import tensorflow as tf

def representative_dataset_gen():
  for _ in range(num_calibration_steps):
    # Get sample input data as a numpy array in a method of your choosing.
    yield [input]

converter = tf.lite.TFLiteConverter.from_saved_model("test")
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = dataset
tflite_model = converter.convert()

with open("lane_navigation.tflite", "wb") as f:
  f.write(tflite_model)
