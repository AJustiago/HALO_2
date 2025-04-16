from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import cv2
import os
import time

import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.image import load_img, img_to_array

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")

# Database and collection
db = client["garbagedb"]
collection = db["garbage"]

# Model Load Resnet Pre-Trained
loaded_model = tf.keras.models.load_model('model_Resnet.h5', compile=False)

# Global Variables
class_mapping = {'metal': 0, 'paper': 1, 'plastic': 2}
IMG_SIZE = (224, 224)

reverse_class_mapping = {v: k for k, v in class_mapping.items()}  

# Image Loading and Preprocessing
def preprocessing_image(image_path, target_size=IMG_SIZE):
    """
    Loads an image and resizes it to the target size.
    :param image_path: Path to the image file.
    :param target_size: Target size for resizing.
    :return: Resized image.
    """
    return load_img(image_path, target_size=target_size)

def insert_data(data):
    """
    Inserts a document into the collection.
    :param data: Dictionary containing the data to insert.
    :return: Inserted document ID.
    """
    insert_result = collection.insert_one(data)
    return insert_result.inserted_id

def get_all_data():
    """
    Retrieves all documents from the collection.
    :return: List of documents.
    """
    return list(collection.find())

@app.route('/run', methods=['POST'])
def run_code():
    data = request.json
    if data.get('value') == 1:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return jsonify({"error": "Could not open webcam."}), 500
        else:
            save_path = "./captured_frames/"

            if not os.path.exists(save_path):
                os.makedirs(save_path)

            time.sleep(5)

            for i in range(1):
                ret, frame = cap.read()
                if not ret:
                    return jsonify({"error": f"Failed to capture frame {i + 1}."}), 500
                else:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{save_path}frame_{timestamp}_{i + 1}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"Saved: {filename}")

                time.sleep(2)

            cap.release()
            cv2.destroyAllWindows()

            image = preprocessing_image(filename)
            image_array = img_to_array(image) / 255.0 
            image_array = np.expand_dims(image_array, axis=0) 

            prediction = loaded_model.predict(image_array)
            predicted_class = np.argmax(prediction, axis=1)

            predicted_label = reverse_class_mapping[predicted_class[0]]
            print(f"Predicted class: {predicted_label}")

            data_to_insert = {
                "label": predicted_label,
                "timestamp": datetime.now()
            }
            
            inserted_id = insert_data(data_to_insert)
            print(f"Data inserted with ID: {inserted_id}")
            
            return jsonify({"message": f"Servo_{predicted_label}"}), 200
    else:
        return jsonify({"error": "Invalid value. Send {'value': 1} to run the code."}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
