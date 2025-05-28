import os
import shutil
import uuid

import magic
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks

from .logic.alignment import create_stacked_image

api_router = APIRouter()
OUTPUT_FOLDER = os.path.join(os.getcwd(), "../output")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

mime_to_extension = {
  "video/mp4": "mp4",
  "video/avi": "avi",
  "video/mkv": "mkv",
  "video/webm": "webm",
  "audio/mpeg": "mp3",
  "image/jpeg": "jpg",
  "image/png": "png",
  "video/quicktime": "mov",
}


def image_path_from_uuid(in_uuid, extension='jpg'):
  image_path = os.path.join(OUTPUT_FOLDER, in_uuid, f"{in_uuid}.{extension}")
  return image_path


@api_router.get("/greet/{name}")
async def greet_user(name: str):
  return {"message": f"Hello, {name}!"}


@api_router.post("/upload")
async def handle_video_upload(background_tasks: BackgroundTasks,
    file: UploadFile = File(...)):
  mime = magic.Magic(mime=True)
  file_type = mime.from_buffer(file.file.read(2048))
  file.file.seek(0)

  if file_type not in ["video/mp4", "video/quicktime"]:
    raise HTTPException(status_code=400, detail="Invalid file format. Only "
                                                "MP4 and MOV are allowed.")

  generated_uuid = str(uuid.uuid4())

  output_dir = os.path.join(OUTPUT_FOLDER, generated_uuid)

  if not os.path.exists(output_dir):
    os.makedirs(output_dir)

  file_extension = mime_to_extension.get(file_type, "")

  if not file_extension:
    return {"error": "Unbekannter MIME-Typ"}

  video_path = os.path.join(output_dir, f'{generated_uuid}.{file_extension}')
  image_path = image_path_from_uuid(generated_uuid)

  with open(video_path, "wb") as buffer:
    shutil.copyfileobj(file.file, buffer)

  background_tasks.add_task(create_stacked_image, video_path, image_path)

  print(output_dir)
  return {"message": "Calculations in progress", "jobId": generated_uuid}


@api_router.get("/status/{job_id}")
async def check_status(job_id: str):
  image_path = image_path_from_uuid(job_id)
  print(image_path)
  if os.path.exists(image_path):
    return {"status": "done", "image_url": f"/output/{job_id}/{job_id}.jpg"}
  return {"status": "processing"}
