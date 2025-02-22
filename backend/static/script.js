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
      statusText.innerHTML = `Upload successful. Job ID: 
                <span id="jobId" style="cursor: pointer; color: blue; text-decoration: underline;">
                    ${result.jobId}`;

      document.getElementById("jobId").addEventListener("click", () => {
        navigator.clipboard.writeText(result.jobId).then(() => {
          alert("Job ID copied to clipboard!");
        }).catch(() => {
          alert("Failed to copy Job ID.");
        });
      });
    } else {
      statusText.textContent = `Upload failed: ${result.detail
      || "Unknown error"}`;
    }
  } catch (error) {
    statusText.textContent = "Network error.";
  }
});
