
# from flask import Flask, render_template, request, redirect, url_for
# from ultralytics import YOLO
# import os
# from werkzeug.utils import secure_filename
# from collections import Counter
# from datetime import datetime

# # Initialize Flask app
# app = Flask(__name__)

# # Folder to save uploaded images
# UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
# app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# # Ensure directories exist
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# # Load your YOLO model
# model = YOLO(r"D:\capstone\trashbag_modelv11\runs\detect\train7\weights\best.pt")  # Replace with your model path

# # Class names as per your model
# class_names = ['Food-garbage', 'Gunnysack', 'Non-Compliant', 'Other', 'Paid-Bag', 'Recycling']

# # List to store upload history
# upload_history = []

# @app.route("/", methods=["GET", "POST"])
# def index():
#     detection_results = None
#     location = None
#     timestamp = None

#     if request.method == "POST":
#         # Handle file upload and object detection
#         if "file" in request.files:
#             file = request.files["file"]
#             if file.filename != "":
#                 filename = secure_filename(file.filename)
#                 file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
#                 file.save(file_path)

#                 # Perform object detection using YOLO
#                 results = model(file_path)

#                 # Extract detected class IDs
#                 detected_classes = [class_names[int(cls)] for cls in results[0].boxes.cls]

#                 # Count occurrences of each class
#                 class_counts = Counter(detected_classes)

#                 # Convert counts to a readable format
#                 detection_results = ", ".join([f"{count} {cls}" for cls, count in class_counts.items()])

#         # Handle location and timestamp
#         if "latitude" in request.form and "longitude" in request.form:
#             latitude = request.form.get("latitude")
#             longitude = request.form.get("longitude")
#             location = f"{latitude}, {longitude}"

#             # Add current timestamp
#             now = datetime.now()
#             timestamp = now.strftime("%I:%M %p %m/%d/%Y")  # Example format: "5:14 AM 11/26/2024"

#             # Calculate total trash bags
#             total_trash_count = sum(Counter(detected_classes).values())

#             # Save the upload data in history
#             upload_data = {
#                 "upload_number": len(upload_history) + 1,
#                 "response": detection_results,
#                 "location": location,
#                 "latitude": float(latitude),
#                 "longitude": float(longitude),
#                 "timestamp": timestamp,
#                 "total_trash": total_trash_count,
#             }
#             upload_history.append(upload_data)

#     return render_template("index.html", detection_results=detection_results, location=location, timestamp=timestamp)


# @app.route("/history")
# def history():
#     return render_template("history.html", upload_history=upload_history)


# @app.route("/map")
# def map_view():
#     return render_template("map.html", upload_history=upload_history)


# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask, render_template, request, redirect, url_for
from ultralytics import YOLO
import os
from werkzeug.utils import secure_filename
from collections import Counter
from datetime import datetime
import requests

# Initialize Flask app
app = Flask(__name__)

# Folder to save uploaded images
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the uploads directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load your YOLO model
model = YOLO('./best.pt')  # Replace with your model's path

# Class names as per your YOLO model
class_names = ['Food-garbage', 'Gunnysack', 'Non-Compliant', 'Other', 'Paid-Bag', 'Recycling']

# List to store upload history
upload_history = []

# Function to get address from KakaoMap
def get_address_from_coordinates_kakao(latitude, longitude):
    api_key = "940ec600d473beb6137e9ed687297f71"  # Use your REST API key
    url = f"https://dapi.kakao.com/v2/local/geo/coord2address.json?x={longitude}&y={latitude}"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    response = requests.get(url, headers=headers)
    data = response.json()

    if "documents" in data and len(data["documents"]) > 0:
        # Return the address from the API response
        address_info = data["documents"][0]["address"]
        return address_info["address_name"]  # e.g., "Seoul, Gangnam-gu, Yeoksam-dong"
    else:
        return "Address not found"

@app.route("/", methods=["GET", "POST"])
def index():
    detection_results = None
    location = None
    timestamp = None

    if request.method == "POST":
        # Handle file upload and object detection
        if "file" in request.files:
            file = request.files["file"]
            if file.filename != "":
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(file_path)

                # Perform object detection using YOLO
                results = model(file_path)
                detected_classes = [class_names[int(cls)] for cls in results[0].boxes.cls]
                class_counts = Counter(detected_classes)
                detection_results = ", ".join([f"{count} {cls}" for cls, count in class_counts.items()])

        # Handle location and timestamp
        if "latitude" in request.form and "longitude" in request.form:
            latitude = float(request.form.get("latitude"))
            longitude = float(request.form.get("longitude"))

            # Get human-readable address using KakaoMap API
            location = get_address_from_coordinates_kakao(latitude, longitude)

            # Add current timestamp
            now = datetime.now()
            timestamp = now.strftime("%I:%M %p %m/%d/%Y")

            # Save the upload data in history
            upload_data = {
                "upload_number": len(upload_history) + 1,
                "response": detection_results,
                "location": location,
                "latitude": latitude,
                "longitude": longitude,
                "timestamp": timestamp,
            }
            upload_history.append(upload_data)

    return render_template("index.html", detection_results=detection_results, location=location, timestamp=timestamp)

@app.route("/history")
def history():
    return render_template("history.html", upload_history=upload_history)

@app.route("/map")
def map_view():
    # Pass upload history as JSON for map rendering
    return render_template("map.html", upload_history=upload_history)

if __name__ == "__main__":
    app.run(debug=True)

