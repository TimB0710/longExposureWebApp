document.getElementById("uploadBtn").addEventListener("click", async () => {
    const fileInput = document.getElementById("videoInput");
    const statusText = document.getElementById("status");

    if (fileInput.files.length === 0) {
        statusText.textContent = "Please choose a video.";
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("video", file);

    try {
        statusText.textContent = "Uploading...";
        const response = await fetch("https://example.com/upload", {
            method: "POST",
            body: formData,
        });

        if (response.ok) {
            statusText.textContent = "Upload successful!";
        } else {
            statusText.textContent = "Upload failed.";
        }
    } catch (error) {
        statusText.textContent = "Network error.";
    }
});
