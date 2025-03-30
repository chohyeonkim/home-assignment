from concurrent.futures import ThreadPoolExecutor
import os
import requests
import time
import mimetypes

# This test simulates 10 concurrent users uploading 100 images each
# to test the backend's ability to handle parallel batch uploads and processing.

# The test:
# - Repeats each image in the 'test_images/' folder 10 times per user (total 100 files/user)
# - Each user sends a single POST request with all files to the /upload endpoint
# - Receives a batch_id in the response from the server
# - Polls the /result/{batch_id} endpoint every 3 seconds
# - Waits up to 180 seconds (3 minutes) for the backend to finish processing
# - Prints the time taken for upload and total time until processing is complete

SERVER_UPLOAD_URL = "http://127.0.0.1:8000/upload"  # force to use ipv4
SERVER_RESULT_URL_TEMPLATE = "http://127.0.0.1:8000/result/{}"
IMAGE_FOLDER = "test_images/"
POLL_INTERVAL = 3
TIMEOUT_LIMIT = 300

# Prepare 100 files per user
def prepare_files():
    files = []
    for i in range(10):
        for filename in os.listdir(IMAGE_FOLDER):
            if filename.endswith((".jpg", ".jpeg", ".png")):
                file_path = os.path.join(IMAGE_FOLDER, filename)
                mime_type, _ = mimetypes.guess_type(file_path)
                unique_name = f"{i}_{filename}"
                files.append(("files", (unique_name, open(file_path, "rb"), mime_type)))
    return files


def simulate_user(user_id):
    start_poll = time.time()
    print(f"User {user_id} starting upload...")
    files = prepare_files()

    start_upload = time.time()
    response = requests.post(SERVER_UPLOAD_URL, files=files)
    upload_time = time.time() - start_upload

    try:
        res = response.json()
    except Exception:
        print(f"[User {user_id}] Failed to parse response:", response.text)
        return

    batch_id = res.get("batch_id")
    if not batch_id:
        print(f"[User {user_id}] No batch_id in response")
        return

    print(
        f"[User {user_id}] Upload complete (Post request) in {upload_time:.2f}s. Polling for result..."
    )

    start_poll = time.time()
    while True:
        elapsed = time.time() - start_poll
        if elapsed > TIMEOUT_LIMIT:
            print(f"[User {user_id}] Timeout after 180s.")
            return

        result_response = requests.get(SERVER_RESULT_URL_TEMPLATE.format(batch_id))
        if result_response.status_code != 200:
            print(f"[User {user_id}] Status code not 200:", result_response.status_code)
            return

        result_data = result_response.json()
        if result_data.get("status") == "completed":
            print(
                f"[User {user_id}] Task completed. Total time: {time.time() - start_upload:.2f}s"
            )
            return
        
        # print("Retrying after 3 seconds")
        time.sleep(POLL_INTERVAL)


def main():
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(simulate_user, i) for i in range(1, 11)]

if __name__ == "__main__":
    main()
