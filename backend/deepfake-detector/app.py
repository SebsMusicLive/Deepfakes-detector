import io
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image

app = FastAPI(title="DeepFake Detector API")

# ===============================
# Configurar CORS
# ===============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # puedes restringir a ["http://localhost:3000"] si deseas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# Cargar modelo
# ===============================
MODEL_PATH = "deepfake_detector_finetuned.keras"

try:
    model = load_model(MODEL_PATH)
    print("✅ Modelo cargado correctamente.")
except Exception as e:
    print(f"❌ Error al cargar el modelo: {e}")

# Tamaño de entrada del modelo
IMG_SIZE = (224, 224)

# ===============================
# Endpoint de prueba
# ===============================
@app.get("/")
def home():
    return {"message": "API de detección de DeepFakes funcionando ✅"}

# ===============================
# Endpoint principal de predicción
# ===============================
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # Leer y procesar imagen
        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
        img = img.resize(IMG_SIZE)

        # Preprocesamiento
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0

        # Predicción
        prediction = model.predict(img_array)
        prob = float(prediction[0][0])

        # Clasificación según umbral
        label = "fake" if prob >= 0.5 else "real"
        confidence = round(prob if label == "fake" else 1 - prob, 4)

        print(f"📸 Imagen procesada -> {label.upper()} ({confidence*100:.2f}%)")

        return JSONResponse({
            "prediction": label,
            "confidence": confidence
        })

    except Exception as e:
        print(f"💥 Error en predicción: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)
