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

## 🐳 Run with Docker (slower than running locally)

1. Make sure Docker is installed and running.
2. Run this from the root directory where `docker-compose.yml` is located.
   ```bash
   docker-compose up --build
   ```

3. The API will be available at:
   ```
   http://localhost:8000/docs
   ```

⚠️ Note: The current implementation uses multiprocessing, creating 4 processes. If the CPU cores allocated to your Docker container are limited, the performance may be significantly slower. In this case, either allocate more CPU cores to your Docker container or run the app locally for better performance.

Alternative option: you can make up for the limited resources by changing `start_workers(4, app.state.job_queue, app.state.results, app.state.lock)` from 4 to 1 or 2. While this may result in lower performance, it will ensure stability, Also you might need to adjust `TIMEOUT_LIMIT` in the test case

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
        |  JoinableQueue   |  ← receives image jobs (1 image per job)
        +--------+--------+
                 |
                 v
        +--------+--------+
        | Background Worker|  ← multiprocessing workers
        |  + YOLOv8 Model  |
        +--------+--------+
                 |
        Segmentation + Area Calculation
                 |
          Store result in memory
                 |
                 v
        +--------+--------+
        |  Results Store   | <- (results[batch_id][data][job_id] = job_result)
        +--------+--------+
                 ^
                 |
    Client polls /result/{batch_id}  <- (results[batch_id])
                 |
          +------+------+
          |   Client    |
          +-------------+

```

## 📌 Notes

- Backend returns a `batch_id` immediately when the `upload_images` endpoint is called by the client.
- Clients poll `/result/{batch_id}` to check result status.
- No persistent storage or cloud services are used — in-memory queue only.
- Designed to run locally on a single machine for simplicity.

## 🧪 Test Results

The following benchmarks compare execution time between local and Dockerized environments.

| Test Script             | Local Run Time with ThreadPoolExecutor | Local Run Time with multiprocessing | Docker Run Time (1 container - ThreadPoolExecutor) |
|-------------------------|----------------------------------------|-------------------------------------| ---------------------------------------------------|
| `upload_search_test.py` | 18 seconds                             | 6 ~ 10 seconds                     | 30 seconds                                         |
| `batch_upload_test.py`  | 159 seconds                            | 56 seconds                          | 283 seconds                                        |

### 🖥️ Test Environment Specs (Local)

- **OS**: Windows 10 Education (64-bit)
- **CPU**: AMD Ryzen 7 5700G (8 cores / 16 threads, 3.8 GHz)
- **RAM**: 32 GB
- **GPU**: AMD Radeon RX 7600 XT (YOLO model loading and prediction were performed on CPU due to unsupported CUDA on AMD GPUs)
- **YOLO Model**: `yolov8n-seg.pt` (Segmentation task, CPU inference)


## 🧰 Setup Summary

| Tool         | Version           |
|--------------|-------------------|
| Python       | 3.10.11           |
| FastAPI      | latest            |
| Docker       | 24+ recommended   |
| YOLOv8       | via `ultralytics` |

