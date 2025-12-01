import io
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
from PIL import Image

app = FastAPI(title="DeepFake Detector API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = "deepfake_detector_finetuned.keras"

try:
    model = load_model(MODEL_PATH)
    print("✅ Modelo cargado correctamente.")
except Exception as e:
    print(f"❌ Error al cargar el modelo: {e}")

IMG_SIZE = (224, 224)

@app.get("/")
def home():
    return {"message": "API de detección de DeepFakes funcionando ✅"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
        img = img.resize(IMG_SIZE)

        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)  # ✅ cambio importante

        prediction = model.predict(img_array)
        prob = float(prediction[0][0])
        print(f"🔍 Valor crudo del modelo: {prob:.4f}")

        # ✅ Lógica corregida: si la probabilidad es ALTA → real
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
