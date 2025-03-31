from fastapi import FastAPI, File, UploadFile
from multiprocessing import Manager, Lock, JoinableQueue, set_start_method
import uuid
from task_runner import (
    create_batch,
    start_workers,
    get_batch_result,
)
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    manager = Manager()
    app.state.results = manager.dict()
    app.state.lock = Lock()
    app.state.job_queue = JoinableQueue()

    start_workers(4, app.state.job_queue, app.state.results, app.state.lock)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/upload")
async def upload_images(files:list[UploadFile] = File(...) ):
    batch_id = str(uuid.uuid4())
    results = app.state.results
    lock = app.state.lock
    job_queue = app.state.job_queue

    create_batch(batch_id, len(files), results, lock)

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
    results = app.state.results
    lock = app.state.lock
    return get_batch_result(batch_id, results, lock)
