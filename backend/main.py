from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="./static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_homepage():
    return FileResponse("./static/index.html")