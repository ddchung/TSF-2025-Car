# Convert from keras to tflite

import tensorflow as tf
from tensorflow import keras

# Load model
model = keras.models.load_model("/Users/tin/AiTestVenv311/test_output_2/lane_navigation_final.keras", compile=False)
model.export("test")

# Convert the model
# Convert the model.
converter = tf.lite.TFLiteConverter.from_saved_model("test")
# converter.experimental_new_converter = False  # Try disabling new converter
tflite_model = converter.convert()

# # Save the model.
with open('lane_navigation.tflite', 'wb') as f:
  f.write(tflite_model)
