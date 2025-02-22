from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import tempfile
import magic
import os
from pathlib import Path

api_router = APIRouter()


@api_router.get("/greet/{name}")
async def greet_user(name: str):
  return {"message": f"Hello, {name}!"}


@api_router.post("/upload")
async def handle_video_upload(file: UploadFile = File(...)):
  mime = magic.Magic(mime=True)
  file_type = mime.from_buffer(file.file.read(2048))
  file.file.seek(0)

  if file_type not in ["video/mp4", "video/quicktime"]:
    raise HTTPException(status_code=400,
                        detail="Invalid file format. Only MP4 and MOV are allowed.")

  try:
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(
        file.filename).suffix) as temp_file:
      temp_path = temp_file.name
      with temp_file as buffer:
        shutil.copyfileobj(file.file, buffer)
        # here function call for algorithm
      job_id = os.path.splitext(os.path.basename(temp_path))[0]
    return {"message": "Calculations in progress", "jobId": job_id}
  except Exception as e:
    return {"error": str(e)}
