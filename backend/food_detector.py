from ultralytics import YOLO
from PIL import Image
import io
import numpy as np
import time

FOOD_CLASSES = {
    "apple",
    "banana",
    "orange",
    "broccoli",
    "carrot",
    "hot dog",
    "pizza",
    "donut",
    "cake",
    "sandwich",
}


model = YOLO("yolov8n-seg.pt")  # use cpu by default (AMD GPU)

### chatgpt - YOLO integration
def run_yolo(image_bytes: bytes) -> dict:
    t1 = time.time()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_np = np.array(image)
    t2 = time.time()

    results = model.predict(img_np, task="segment", verbose=False)[0]  # bottleneck
    t3 = time.time()
    food_areas = {}
    for i, cls_id in enumerate(results.boxes.cls.cpu().numpy()):
        class_name = model.names[int(cls_id)]

        if class_name not in FOOD_CLASSES:
            continue

        mask = results.masks.data[i].cpu().numpy()
        area = int(np.sum(mask))

        food_areas[class_name] = food_areas.get(class_name, 0) + area
    t4 = time.time()

    print(
        f"[run_yolo] image_decode: {t2 - t1:.2f}s, "
        f"inference: {t3 - t2:.2f}s, "
        f"postproc: {t4 - t3:.2f}s, "
        f"total: {t4 - t1:.2f}s"
    )

    return food_areas
