import tensorflow as tf
from tensorflow import keras
import cv2
import glob
import numpy as np

IMG_SIZE = (66, 200)
IMG_CHANNELS = 1

image_paths = glob.glob("lane_nav_data/*.jpg")

def dataset():
  for img in image_paths:
    img = cv2.imread(img, cv2.IMREAD_GRAYSCALE)  # Read in grayscale
    img = cv2.resize(img, IMG_SIZE)  # Resize to model input size
    img = np.expand_dims(img, axis=-1)  # Add channel dimension (H, W, 1)
    img = np.expand_dims(img, axis=0)  # Add batch dimension (1, H, W, 1)
    img = img.astype(np.float32) / 255.0  # Normalize (if needed)
    yield [img]

model = keras.models.load_model("lane_nav_model_final.keras", compile=False)
model.export("test")

converter = tf.lite.TFLiteConverter.from_saved_model("test")
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = dataset
# Ensure that if any ops can't be quantized, the converter throws an error
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
# Set the input and output tensors to uint8 (APIs added in r2.3)
converter.inference_input_type = tf.uint8
converter.inference_output_type = tf.uint8
tflite_model = converter.convert()

with open("lane_nav.tflite", "wb") as f:
  f.write(tflite_model)
