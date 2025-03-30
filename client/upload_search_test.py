import os
import requests
import time
import mimetypes

# This test simulates a single user uploading 100 images at once
# to test the backend's ability to handle batch upload and processing.

# The test:
# - Loads 100 images (10 repeats of each image in 'test_images/' folder)
# - Sends all images in a single POST request to the /upload endpoint
# - Receives a batch_id immediately from the server
# - Polls the /result/{batch_id} endpoint every 2 seconds
# - Waits up to 60 seconds for the backend to complete processing
# - Once processing is complete, it prints the job IDs and area results for each food item


SERVER_UPLOAD_URL = "http://127.0.0.1:8000/upload"  # force to use ipv4
IMAGE_FOLDER = "test_images/"

files = []
for i in range(10):
    for filename in os.listdir(IMAGE_FOLDER):
        if filename.endswith((".jpg", ".jpeg", ".png")):
            file_path = os.path.join(IMAGE_FOLDER, filename)
            mime_type, _ = mimetypes.guess_type(file_path)
            unique_name = f"{i}_{filename}"
            files.append(("files", (unique_name, open(file_path, "rb"), mime_type)))

start_test_time = time.time()
response = requests.post(SERVER_UPLOAD_URL, files=files)
# print(f"Takes {time.time() - start_test_time} after Post")

try:
    res = response.json()
    print("Response:", response.json())
    print("Status Code:", response.status_code)
except Exception:
    print("Error", response.text)

BATCH_ID = res["batch_id"]
SERVER_RESULT_URL = f"http://127.0.0.1:8000/result/{BATCH_ID}" # force to use ipv4
POLL_INTERVAL = 2
TIMEOUT_LIMIT = 60
start_time = time.time()

while True:
    elasped = time.time() - start_time

    if elasped > TIMEOUT_LIMIT:
        print("Time out - 60s")
        print("Result:", res)
        break

    try:
        # print(f"Takes {time.time() - start_time} before get")
        response = requests.get(SERVER_RESULT_URL)
        # print(f"Takes {time.time() - start_time} after get")
    except Exception as e:
        print("Failed request", str(e))
        break

    if response.status_code != 200:
        print("Status code is not 200")
        break

    res = response.json()
    if res["status"] == "completed":
        for job_id in res["data"]:
            print("job_id:", job_id)
            for food, val in res["data"][job_id].items():
                print(f"{food}:{val}\n") 
        break

    print("Retrying after 2 seconds")
    time.sleep(POLL_INTERVAL)     

test_time = time.time() - start_test_time

print(f"Takes {test_time} second for the whole test ")
