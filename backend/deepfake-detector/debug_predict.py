# debug_predict.py
import sys, os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image

MODEL_PATH = "deepfake_detector_finetuned.keras"  # ajustar si es otro

def load_img(path, size=(224,224)):
    img = Image.open(path).convert("RGB").resize(size)
    arr = np.array(img).astype("float32") / 255.0
    return np.expand_dims(arr, 0)

def main():
    if len(sys.argv) < 3:
        print("Uso: python debug_predict.py <imagen_real> <imagen_fake>")
        return
    model = load_model(MODEL_PATH)
    print("Modelo cargado:", MODEL_PATH)
    for p in sys.argv[1:]:
        x = load_img(p)
        prob = float(model.predict(x)[0][0])
        print(f"{os.path.basename(p)} -> prob cruda: {prob:.6f}")

if __name__ == "__main__":
    main()
