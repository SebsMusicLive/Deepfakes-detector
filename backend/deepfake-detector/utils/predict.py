import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import pandas as pd
from datetime import datetime

# Ruta del modelo entrenado
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'deepfake_detector_finetuned.keras')
HISTORY_PATH = os.path.join(os.path.dirname(__file__), '..', 'predictions_history.csv')

# Cargar modelo (solo una vez)
print("🔄 Cargando modelo de deepfake...")
model = tf.keras.models.load_model(MODEL_PATH)
print("✅ Modelo cargado correctamente.")

# Función de predicción
def predict_image(img_path):
    """Recibe una imagen y devuelve si es real o fake junto con su confianza"""
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Predicción
    prob = float(model.predict(img_array, verbose=0)[0][0])
    label = "real" if prob < 0.5 else "fake"
    confidence = round(1 - prob if label == "real" else prob, 4)

    # Guardar resultado en historial
    log_prediction(img_path, label, confidence)

    return {"prediction": label, "confidence": confidence}

def log_prediction(img_path, label, confidence):
    """Guarda la predicción en un CSV de historial"""
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "image_name": os.path.basename(img_path),
        "prediction": label,
        "confidence": confidence
    }
    df = pd.DataFrame([data])

    if not os.path.exists(HISTORY_PATH):
        df.to_csv(HISTORY_PATH, index=False)
    else:
        df.to_csv(HISTORY_PATH, mode='a', index=False, header=False)

# Para pruebas directas desde consola
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("❌ Uso: python predict.py <ruta_imagen>")
    else:
        img_path = sys.argv[1]
        result = predict_image(img_path)
        print(f"\n🧩 Resultado -> {result}\n")
