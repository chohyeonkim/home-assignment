import queue
from food_detector import run_yolo
from concurrent.futures import ThreadPoolExecutor
import threading
import time

# results = {
#     batch_id: {
#         "status": str,            # "processing" | "completed"
#         "remaining": int,         # remaining jobs in batch
#         "data": {
#             job_id: {
#                 label (str): int  # e.g., "pizza": 1200
#             }
#         }
#     }
# }

results = {} 
job_queue = queue.Queue()
executor = ThreadPoolExecutor(max_workers=5)
lock = threading.Lock()

def create_batch(batch_id: str, flies_length: int):
    with lock:
        results[batch_id] = {
            "status": "pending",
            "remaining": flies_length,
            "data": {},
        }

def get_batch_result(batch_id: str):
    with lock:
        res = results[batch_id]
    return res

def store_job_result(batch_id: str, job_id: str, res: dict):
    with lock:
        results[batch_id]["data"][job_id] = res
        results[batch_id]["remaining"] -= 1

        if results[batch_id]["remaining"] == 0:
            results[batch_id]["status"] = "completed"

def worker():
    while True:
        batch_id, job_id, image_bytes = job_queue.get()
        start_time = time.time()
        print(f"[worker] Process batch_id={batch_id}, job_id={job_id}")
        try :
            res = run_yolo(image_bytes)
        except Exception as e:
            print("[worker] Image processing Error: ", e)
            res = {"error": str(e)}

        store_job_result(batch_id=batch_id, job_id=job_id, res=res)
        job_queue.task_done()
        
        end_time = time.time() - start_time
        print(f"[worker] Finished job_id ={job_id}, takes {end_time:.2f}s")

def start_workers(workers):
    for _ in range(workers):
        executor.submit(worker)
