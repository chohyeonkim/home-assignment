from food_detector import run_yolo
import multiprocessing
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

def create_batch(batch_id, flies_length, results, lock):
    with lock:
        results[batch_id] = {
            "status": "pending",
            "remaining": flies_length,
            "data": {},
        }


def get_batch_result(batch_id, results, lock):
    with lock:
        return results[batch_id]


def store_job_result(batch_id, job_id, res, results, lock):
    with lock:
        batch = results[batch_id]

        new_data = dict(batch["data"]) # nested dict can be proxy as well -> copy 
        new_data[job_id] = res

        batch["remaining"] -= 1
        if batch["remaining"] == 0:
            batch["status"] = "completed"

        # Manager dict not track nested changes, so reassign the whole value
        results[batch_id] = {
            "status": batch["status"],
            "remaining": batch["remaining"],
            "data": new_data,
        }


def worker(job_queue, results, lock):
    while True:
        batch_id, job_id, image_bytes = job_queue.get()
        start_time = time.time()
        print(f"[worker] Process batch_id={batch_id}, job_id={job_id}")
        try:
            res = run_yolo(image_bytes)
        except Exception as e:
            print("[worker] Image processing Error:", e)
            res = {"error": str(e)}

        store_job_result(batch_id, job_id, res, results, lock)
        job_queue.task_done()
        end_time = time.time() - start_time
        print(f"[worker] Finished job_id={job_id}, takes {end_time:.2f}s")


def start_workers(workers, job_queue, results, lock):
    for _ in range(workers):
        p = multiprocessing.Process(target=worker, args=(job_queue, results, lock))
        p.daemon = True
        p.start()
