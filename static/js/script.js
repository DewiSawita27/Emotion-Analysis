const previewBox = document.getElementById("preview");
const cameraBtn = document.getElementById("cameraBtn");
const uploadBtn = document.getElementById("uploadBtn");
const analyzeBtn = document.getElementById("analyzeBtn");


const cameraStream = document.getElementById("cameraStream");
const captureBtn = document.getElementById("captureBtn");

let videoStream = null;
let capturedImage = null;


let deleteBtn = document.createElement("button");
deleteBtn.innerHTML = "✖";
deleteBtn.classList.add("delete-btn");
deleteBtn.style.display = "none";
previewBox.appendChild(deleteBtn);


cameraBtn.addEventListener("click", async () => {
    try {
        videoStream = await navigator.mediaDevices.getUserMedia({ video: true });

        cameraStream.style.display = "block";
        cameraStream.srcObject = videoStream;

        previewBox.innerHTML = "";
        previewBox.appendChild(cameraStream);
        previewBox.appendChild(captureBtn);
        previewBox.appendChild(deleteBtn);

        captureBtn.style.display = "block";
        deleteBtn.style.display = "block";

    } catch (error) {
        alert("Kamera tidak bisa diakses!");
        console.error(error);
    }
});


captureBtn.addEventListener("click", () => {
    if (!videoStream) return;

    const canvas = document.createElement("canvas");
    canvas.width = cameraStream.videoWidth;
    canvas.height = cameraStream.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(cameraStream, 0, 0);

    canvas.toBlob((blob) => {
        capturedImage = blob;

        previewBox.innerHTML = `
            <img src="${URL.createObjectURL(blob)}" class="preview-img">
        `;
        previewBox.appendChild(deleteBtn);
        deleteBtn.style.display = "block";

        stopCamera();
    }, "image/jpeg");
});


function stopCamera() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }
    cameraStream.style.display = "none";
    captureBtn.style.display = "none";
}


uploadBtn.addEventListener("click", () => {
    let input = document.createElement("input");
    input.type = "file";
    input.accept = "image/*";

    input.onchange = () => {
        const file = input.files[0];
        if (!file) return;

        capturedImage = file;

        previewBox.innerHTML = `
            <img src="${URL.createObjectURL(file)}" class="preview-img">
        `;
        previewBox.appendChild(deleteBtn);
        deleteBtn.style.display = "block";

        stopCamera();
    };

    input.click();
});


deleteBtn.addEventListener("click", () => {
    capturedImage = null;
    previewBox.innerHTML = "<p>Tidak ada gambar</p>";
    deleteBtn.style.display = "none";

    stopCamera();
});


analyzeBtn.addEventListener("click", () => {
    if (!capturedImage) {
        alert("Ambil foto atau upload foto terlebih dahulu!");
        return;
    }

    let formData = new FormData();
    formData.append("image", capturedImage, "input.jpg");

    fetch("/analyze", {
        method: "POST",
        body: formData
    })
        .then(res => res.text())
        .then(html => {
            document.open();
            document.write(html);
            document.close();
        })
        .catch(err => {
            console.error(err);
            alert("Terjadi kesalahan saat mengirim gambar.");
        });
});