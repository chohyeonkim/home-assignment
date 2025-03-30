# food-segmentation-server
A scalable backend application for detecting and segmenting food items in images, then calculating their area.  
Built using FastAPI and YOLOv8. Designed to support asynchronous image processing and horizontal scaling via Docker.

---

## ⚙️ Development Workflow

- **Backend**: FastAPI (Python 3.10.11)
- **Image Processing**: YOLOv8 (via Ultralytics)
- **Containerization**: Docker & Docker Compose
- **Client**: Local Python script (`batch_upload_test.py, upload_search_test.py`) to send requests

## 🚀 Getting Started (Local Development)

### 🔧 Requirements

- Python 3.10+
- pip
- (Optional) Docker & Docker Compose

### 🧪 Run Backend Locally (without Docker)


1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

2. (Optional) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the FastAPI server:
   ```bash
   fastapi dev backend/main.py
   ```

## 🐳 Run with Docker (may be slower than running locally)

1. Make sure Docker is installed and running.
2. Run this from the root directory where `docker-compose.yml` is located.
   ```bash
   docker-compose up --build
   ```

3. The API will be available at:
   ```
   http://localhost:8000/docs
   ```

## 📤 Sending Requests (Client)

- The client script (`client/batch_upload_test.py`, `client/upload_search_test.py` ) is not containerized — it runs locally from your host machine to send requests to the backend.

- You can send requests manually from your local environment:
   ```bash
   cd client
   python upload_search_test.py
   ```

## 🧱 Architecture Overview

```
          +-------------+
          |   Client    |   (Python script: upload_search_test.py)
          +------+------+
                 |
         HTTP POST /upload_images
                 |
                 v
          +------+------+
          |  FastAPI     |  (REST API)
          |  Backend     |
          +------+------+
                 |
            Enqueue job 
         and return batch_id
                 |
                 v
        +--------+--------+
        |  queue.Queue     |  
        +--------+--------+
                 |
                 v
        +--------+--------+
        | Background Worker|  (ThreadPoolExecutor)
        |  + YOLOv8 Model  |
        +--------+--------+
                 |
        Segmentation + Area Calculation
                 |
          Store result in memory
                 |
                 v
        +--------+--------+
        |  Results Store   |  (results[batch_id][data] = results)
        +--------+--------+
                 ^
                 |
    Client polls /result/{batch_id}
                 |
          +------+------+
          |   Client    |
          +-------------+

```

## 📌 Notes

- This server supports **horizontal scaling** via Docker Compose.
- Backend returns a `batch_id` immediately when the `upload_images` endpoint is called by the client.
- Clients poll `/result/{batch_id}` to check result status.
- No persistent storage or cloud services are used — in-memory queue only.
- Designed to run locally on a single machine for simplicity.

## 🧪 Test Results

The following benchmarks compare execution time between local and Dockerized environments.

| Test Script             | Local Run Time | Docker Run Time (1 container) |
|-------------------------|----------------|-------------------------------|
| `upload_search_test.py` | 18 seconds     | 30 seconds                    |
| `batch_upload_test.py`  | 159 seconds    | 283 seconds                   |

## 🧰 Setup Summary

| Tool         | Version           |
|--------------|-------------------|
| Python       | 3.10.11           |
| FastAPI      | latest            |
| Docker       | 24+ recommended   |
| YOLOv8       | via `ultralytics` |

