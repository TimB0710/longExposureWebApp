# Video Processing API with FastAPI and Frontend

This project provides a FastAPI-based backend for uploading and processing video files, along with a simple frontend for interaction. The backend supports video uploads, job ID tracking, and polling to check processing status. Once processing is complete, the output image is made available for download.

## Features
- Upload video files (MP4 and MOV supported)
- Generate a job ID for tracking
- Periodically check processing status (polling mechanism)
- Serve processed images as static files
- Simple JavaScript-based frontend

---

## Installation & Setup

### 1. **Clone the Repository**
```bash
git clone https://github.com/TimB0710/longExposureWebApp.git
cd longExposureWebApp
```

### 2. **Set up a Virtual Environment (optional but recommended)**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. **Install Dependencies**
```bash
pip install fastapi uvicorn python-magic pathlib shutil tempfile
```

---

## Backend (FastAPI)

### **1. FastAPI Server**
The backend handles video uploads and processing. It provides two main endpoints:

#### **Upload a Video**
**Endpoint:** `POST /api/upload`
- Accepts a video file (MP4, MOV)
- Generates a `jobId`
- Saves the file temporarily and triggers processing
- Returns: `{ "message": "Calculations in progress", "jobId": "some-id" }`

#### **Check Processing Status**
**Endpoint:** `GET /api/status/{jobId}`
- Checks if the processed image exists
- If processing is done, returns `{ "status": "done", "image_url": "/output/{jobId}.png" }`
- If still processing, returns `{ "status": "processing" }`

### **2. Serving Processed Images**
To make the processed image accessible, FastAPI serves static files:
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from my_routes import api_router

app = FastAPI()

OUTPUT_FOLDER = "output_images"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
app.mount("/output", StaticFiles(directory=OUTPUT_FOLDER), name="output")

app.include_router(api_router)
```

---

## Frontend (JavaScript + HTML)

### **1. File Upload & Status Check**
The frontend consists of a simple HTML page with JavaScript logic:

- **Uploads video files to `/api/upload`**
- **Starts polling `/api/status/{jobId}` every 5 seconds**
- **Displays the processed image when ready**

#### **Frontend Code (static/script.js)**
```javascript
document.getElementById("uploadBtn").addEventListener("click", async () => {
    const fileInput = document.getElementById("videoInput");
    const statusText = document.getElementById("status");

    if (fileInput.files.length === 0) {
        statusText.textContent = "Please choose a video.";
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    try {
        statusText.textContent = "Uploading...";
        const response = await fetch("/api/upload", {
            method: "POST",
            body: formData,
        });

        const result = await response.json();

        if (response.ok) {
            const jobId = result.jobId;
            statusText.innerHTML = `Upload successful. Job ID:
                <span id="jobId" style="cursor: pointer; color: blue; text-decoration: underline;">
                    ${jobId}
                </span> (Checking status...)`;

            document.getElementById("jobId").addEventListener("click", () => {
                navigator.clipboard.writeText(jobId).then(() => {
                    alert("Job ID copied to clipboard!");
                }).catch(() => {
                    alert("Failed to copy Job ID.");
                });
            });

            // Start polling
            checkStatus(jobId);
        } else {
            statusText.textContent = `Upload failed: ${result.detail || "Unknown error"}`;
        }
    } catch (error) {
        statusText.textContent = "Network error.";
    }
});

async function checkStatus(jobId) {
    const statusText = document.getElementById("status");

    const interval = setInterval(async () => {
        const response = await fetch(`/api/status/${jobId}`);
        const result = await response.json();

        if (result.status === "done") {
            clearInterval(interval);
            statusText.innerHTML = `Processing complete!
                <a href="${result.image_url}" target="_blank">Download result</a>`;
        }
    }, 5000);
}
```

#### **HTML Structure (index.html)**
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Video Upload</title>
  <link rel="stylesheet" href="./static/styles.css">
</head>
<body>
<div class="container">
  <h2>Upload Video</h2>
  <input type="file" id="videoInput" accept="video/*">
  <button id="uploadBtn">Upload</button>
  <p id="status"></p>
</div>
<script src="./static/script.js"></script>
</body>
</html>
```

---

## **How It Works**
1. **User uploads a video** → The backend assigns a `jobId` and starts processing.
2. **Frontend starts polling `/api/status/{jobId}`** every 5 seconds.
3. **When processing is complete**, the backend returns `{ "status": "done", "image_url": "/output/{jobId}.png" }`.
4. **Frontend displays a link to the processed image.**

---

## **Running the Application**

### **Start the FastAPI Server**
```bash
cd .\backend/
# for development 
fastapi dev .\main.py --port 8000
# for prod
fastapi run .\main.py --host 0.0.0.0 --port 8000
```

## **Future Improvements**
- Use **WebSockets** instead of polling for real-time updates.
- Add support for **more video formats**.
- Improve UI/UX with better **status indicators**.