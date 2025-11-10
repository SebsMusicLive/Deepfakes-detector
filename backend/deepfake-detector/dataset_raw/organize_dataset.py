import os
import shutil

ROOT = "dataset_raw"
DEST = "dataset"

# Buscar carpeta que contiene 'training_real'
source_folder = None
for root, dirs, files in os.walk(ROOT):
    if "training_real" in dirs and "training_fake" in dirs:
        source_folder = root
        break

if not source_folder:
    raise FileNotFoundError("No se encontraron las carpetas training_real / training_fake dentro de dataset_raw.")

print(f"✅ Carpeta base detectada automáticamente: {source_folder}")

# Crear carpetas destino
os.makedirs(os.path.join(DEST, "real"), exist_ok=True)
os.makedirs(os.path.join(DEST, "fake"), exist_ok=True)

def move_files(src_dir, dst_dir):
    count = 0
    for file in os.listdir(src_dir):
        src = os.path.join(src_dir, file)
        dst = os.path.join(dst_dir, file)
        if os.path.isfile(src):
            shutil.copy(src, dst)
            count += 1
    print(f"✅ {count} archivos copiados desde {src_dir} → {dst_dir}")

move_files(os.path.join(source_folder, "training_real"), os.path.join(DEST, "real"))
move_files(os.path.join(source_folder, "training_fake"), os.path.join(DEST, "fake"))

print("\n🎯 Dataset organizado correctamente en la carpeta /dataset")
