from fastapi import FastAPI, File, UploadFile
import uuid
from task_runner import (
    create_batch,
    job_queue,
    start_workers,
    get_batch_result,
)
import time

app = FastAPI()
start_workers(workers=4)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/upload")
async def upload_images(files:list[UploadFile] = File(...) ):
    batch_id = str(uuid.uuid4())
    create_batch(batch_id, len(files))

    for file in files:
        job_id = str(uuid.uuid4())
        try:
            content = await file.read()
        except Exception as e:
            print("[upload_images] File upload Error: ", e)

        job_queue.put((batch_id, job_id, content))
        print(f" [upload_images] job_id={job_id} added. Current queue size: {job_queue.qsize()}")

    return {"batch_id": batch_id}

@app.get("/result/{batch_id}")
def batch_result(batch_id: str):
    res = get_batch_result(batch_id)
    return res
