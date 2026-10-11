from flask import Flask, render_template, request, redirect, send_file
from werkzeug.utils import secure_filename
import os
import uuid
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# Folder upload
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Load model
model = load_model("model/model_emotion.keras")

# Label ekspresi
labels = ["Angry", "Fear", "Happy", "Sad"]

# Halaman utama
@app.route("/")
def index():
    return render_template("index.html")

# Proses Upload & Analisis
@app.route("/analyze", methods=["POST"])
def analyze():
    # menerima file dari frontend
    if "image" not in request.files:
        return redirect("/")

    img_file = request.files["image"]

    if img_file.filename == "":
        return redirect("/")

    # Simpan dengan nama unik
    filename = str(uuid.uuid4()) + ".jpg"
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    img_file.save(save_path)

    # PREPROCESS IMAGE
    img = image.load_img(save_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0

    # Prediksi
    preds = model.predict(img_array)[0]
    pred_idx = np.argmax(preds)
    pred_label = labels[pred_idx]
    pred_percent = float(np.max(preds) * 100)

    indikasi = {
        "Angry": "Emosimu mungkin sedang memuncak atau tertekan.",
        "Fear": "Ada kemungkinan kamu sedang merasa cemas atau terancam.",
        "Happy": "Kondisi psikologismu menunjukkan suasana hati positif.",
        "Sad": "Kamu mungkin sedang mengalami tekanan emosional."
    }

    solusi = {
        "Angry": "Tenangkan diri sebelum mengambil keputusan.",
        "Fear": "Ambil napas dalam-dalam dan coba relaksasi.",
        "Happy": "Pertahankan suasana positif dan tetap produktif.",
        "Sad": "Coba ceritakan perasaanmu ke orang yang kamu percaya."
    }

    return render_template(
        "result.html",
        image_path=save_path,
        ekspresi=pred_label,
        persen=round(pred_percent, 2),
        indikasi=indikasi[pred_label],
        solusi=solusi[pred_label]
    )

# Download PDF
@app.route("/download")
def download():
    ekspresi = request.args.get("ekspresi")
    persen = request.args.get("persen")
    indikasi = request.args.get("indikasi")
    solusi = request.args.get("solusi")

    pdf_path = "static/result.pdf"
    doc = SimpleDocTemplate(pdf_path)
    styles = getSampleStyleSheet()

    content = [
        Paragraph(f"<b>Hasil Analisis Ekspresi Wajah</b>", styles["Title"]),
        Paragraph(f"Ekspresi: {ekspresi}", styles["Normal"]),
        Paragraph(f"Persentase: {persen} %", styles["Normal"]),
        Paragraph(f"Indikasi: {indikasi}", styles["Normal"]),
        Paragraph(f"Solusi: {solusi}", styles["Normal"]),
    ]

    doc.build(content)

    return send_file(pdf_path, as_attachment=True)


# Run App
if __name__ == "__main__":
    app.run(debug=True)

#p