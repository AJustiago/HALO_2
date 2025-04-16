import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 

import streamlit as st
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.image import img_to_array, load_img


with st.sidebar:
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("HALO.png", width=80)
    with col2:
        st.markdown("## HALO")
        

# Title and description
st.title("Image Trash Classification")
st.write("""
This app classifies trash into **three categories**: **Paper**, **Plastic**, and **Metal**.  
Simply upload an image of a trash item and the model will predict which type it belongs to.
""")

# Global Variables
class_mapping = {'metal': 0, 'paper': 1, 'plastic': 2}
IMG_SIZE = (224, 224)
reverse_class_mapping = {v: k for k, v in class_mapping.items()}

# Preprocessing function
def preprocessing_image(image_file):
    return load_img(image_file, target_size=IMG_SIZE)

# Upload image
uploaded_file = st.file_uploader("Upload an image of trash", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    print("test: ", uploaded_file)
    image = preprocessing_image(uploaded_file)
    image_array = img_to_array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0)

    try:
        loaded_model = tf.keras.models.load_model('model_Resnet.h5', compile=False)
    except Exception as e:
        st.error(f"Error loading model: {e}")
        st.stop()

    
    prediction = loaded_model.predict(image_array)
    predicted_class_index = int(np.argmax(prediction, axis=1)[0])
    predicted_label = reverse_class_mapping[predicted_class_index]

    st.subheader("Prediction")
    st.success(f"The model predicts this is: **{predicted_label.capitalize()}**")

    confidence = float(np.max(prediction))
    st.info(f"Confidence: {confidence * 100:.2f}%")
