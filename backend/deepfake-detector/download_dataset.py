
import os
import zipfile
import kaggle

# ==========================
# CONFIGURACIÓN
# ==========================
DATASET = "ciplab/real-and-fake-face-detection"
DOWNLOAD_PATH = "dataset_raw"
EXTRACT_PATH = "dataset"

# ==========================
# DESCARGA DEL DATASET
# ==========================
os.makedirs(DOWNLOAD_PATH, exist_ok=True)
print("📦 Descargando dataset desde Kaggle...")

kaggle.api.dataset_download_files(DATASET, path=DOWNLOAD_PATH, unzip=True)
print("✅ Descarga completada.")

# ==========================
# ORGANIZAR LAS CARPETAS
# ==========================
print("📂 Organizando imágenes en carpetas /real y /fake...")

os.makedirs(os.path.join(EXTRACT_PATH, "real"), exist_ok=True)
os.makedirs(os.path.join(EXTRACT_PATH, "fake"), exist_ok=True)

# La estructura original del dataset contiene:
#   real_and_fake_face/real/
#   real_and_fake_face/fake/
root_path = os.path.join(DOWNLOAD_PATH, "real_and_fake_face")

for category in ["real", "fake"]:
    src_folder = os.path.join(root_path, category)
    dest_folder = os.path.join(EXTRACT_PATH, category)
    if os.path.exists(src_folder):
        for file in os.listdir(src_folder):
            src = os.path.join(src_folder, file)
            dst = os.path.join(dest_folder, file)
            os.rename(src, dst)

print("✅ Dataset organizado correctamente en la carpeta /dataset")
print("Estructura final:")
print("  dataset/real/...")
print("  dataset/fake/...")
