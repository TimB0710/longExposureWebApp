from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from api.routes import api_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="./static"), name="static")

OUTPUT_FOLDER = "../output"
app.mount("/output", StaticFiles(directory=OUTPUT_FOLDER), name="output")

app.include_router(api_router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
async def serve_homepage():
  return FileResponse("./static/index.html")
