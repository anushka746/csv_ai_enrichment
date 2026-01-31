// script.js

// 👉 Replace this with your FastAPI endpoint
const API_URL = "http://127.0.0.1:8000/upload_file";

const sourceColumnInput = document.getElementById("sourceColumn");
const newColumnInput = document.getElementById("newColumn");
const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const browseBtn = document.getElementById("browseBtn");
const fileInfo = document.getElementById("fileInfo");
const processBtn = document.getElementById("processBtn");
const loader = document.getElementById("loader");
const message = document.getElementById("message");
const sourceColumn = sourceColumnInput.value.trim();
const newColumn = newColumnInput.value.trim();



let selectedFile = null;

/* ---------- Drag & Drop ---------- */
["dragenter", "dragover"].forEach(event => {
  dropzone.addEventListener(event, e => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });
});

["dragleave", "drop"].forEach(event => {
  dropzone.addEventListener(event, e => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
  });
});

dropzone.addEventListener("drop", e => {
  handleFile(e.dataTransfer.files[0]);
});
dropzone.addEventListener("click", () => {
  fileInput.click();
});

fileInput.addEventListener("change", e => handleFile(e.target.files[0]));

/* ---------- File Handling ---------- */
function handleFile(file) {
  resetMessage();

  if (!file || !file.name.trim().toLowerCase().endsWith(".csv")) {
    showMessage("Please upload a valid .csv file", "error");
    return;
  }

  selectedFile = file;
  fileInfo.textContent = `Selected file: ${file.name}`;
  fileInfo.classList.remove("hidden");
  processBtn.disabled = false;
}

/* ---------- Process CSV ---------- */
processBtn.addEventListener("click", async () => {
  if (!selectedFile) return;
  
  const sourceColumn = sourceColumnInput.value.trim();
  const newColumn = newColumnInput.value.trim();
  if (!sourceColumn || !newColumn) {
  showMessage("Please enter both column names.", "error");
  return;
}


  toggleLoading(true);
  processBtn.disabled = true;

const formData = new FormData();
formData.append("file", selectedFile);
formData.append("columns", sourceColumn);
formData.append("new_columns", newColumn);


  try {
    const response = await fetch(API_URL, {
      method: "POST",
      body: formData
    });

    const contentType = response.headers.get("content-type");
    
    
    if (contentType && contentType.includes("application/json")) {
      const data = await response.json();
      showMessage(data.message, data.status === "error" ? "error" : "info");
      return; 
    }

    if (!response.ok) {
      throw new Error("Processing failed");
    }

    const blob = await response.blob();
    showMessage("CSV processed successfully!", "success");
    triggerDownload(blob);

  } catch (err) {
    console.log(err)
    showMessage("Something went wrong. Please try again.", "error");
  } finally {
    toggleLoading(false);
    processBtn.disabled = false;
  }
});

/* ---------- Helpers ---------- */
function toggleLoading(state) {
  loader.classList.toggle("hidden", !state);
}

function showMessage(text, type) {
  message.textContent = text;
  message.className = `message ${type}`;
  message.classList.remove("hidden");
}

function resetMessage() {
  message.classList.add("hidden");
}

function triggerDownload(blob) {
  const url = URL.createObjectURL(blob);
  setTimeout(() => {
    const a = document.createElement("a");
    a.href = url;
    a.download = "updated.csv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, 600);
}
