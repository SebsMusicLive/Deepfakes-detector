import os
import matplotlib.pyplot as plt
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

# ==========================================================
# CONFIGURACIÓN DEL ENTORNO Y DATASET
# ==========================================================
BASE_DIR = os.path.join("dataset_raw", "real_and_fake_face_detection")
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS_BASE = 10       # Entrenamiento inicial con capas congeladas
EPOCHS_FINE = 10       # Fine-tuning (capas descongeladas)

# ==========================================================
# PREPROCESAMIENTO Y GENERADORES DE IMAGEN
# ==========================================================
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=25,
    zoom_range=0.2,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True,
    validation_split=0.2
)

train_generator = train_datagen.flow_from_directory(
    BASE_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='binary',
    subset='training'
)

val_generator = train_datagen.flow_from_directory(
    BASE_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='binary',
    subset='validation'
)

# ==========================================================
# MODELO BASE (ResNet50)
# ==========================================================
base_model = ResNet50(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3)
)

# Congelar capas para la fase inicial
for layer in base_model.layers:
    layer.trainable = False

# Construcción del modelo final
model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    Dropout(0.4),
    Dense(128, activation='relu'),
    Dropout(0.3),
    Dense(1, activation='sigmoid')  # Salida binaria (real/fake)
])

# ==========================================================
# FASE 1: ENTRENAMIENTO BASE
# ==========================================================
model.compile(
    optimizer=Adam(learning_rate=1e-3),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

callbacks_base = [
    EarlyStopping(patience=3, restore_best_weights=True, monitor='val_loss'),
    ReduceLROnPlateau(factor=0.2, patience=2, min_lr=1e-6),
    ModelCheckpoint('best_model_base.keras', save_best_only=True)
]

print("\n🚀 Entrenando modelo base (capas congeladas)...\n")

history_base = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=EPOCHS_BASE,
    callbacks=callbacks_base
)

# ==========================================================
# FASE 2: FINE-TUNING
# ==========================================================
print("\n🎯 Iniciando Fine-Tuning...\n")

# Descongelar las últimas capas de la ResNet50 para afinar
for layer in base_model.layers[-30:]:
    layer.trainable = True

# Recompilar con una tasa de aprendizaje menor
model.compile(
    optimizer=Adam(learning_rate=1e-5),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

callbacks_ft = [
    EarlyStopping(patience=3, restore_best_weights=True, monitor='val_loss'),
    ReduceLROnPlateau(factor=0.3, patience=2, min_lr=1e-7),
    ModelCheckpoint('best_model_finetuned.keras', save_best_only=True)
]

history_fine = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=EPOCHS_FINE,
    callbacks=callbacks_ft
)

# ==========================================================
# GUARDAR MODELO FINAL
# ==========================================================
model.save('deepfake_detector_finetuned.keras')
print("\n✅ Modelo final guardado como 'deepfake_detector_finetuned.keras'\n")

# ==========================================================
# VISUALIZACIÓN DE MÉTRICAS
# ==========================================================
plt.figure(figsize=(8, 5))
plt.plot(history_base.history['loss'] + history_fine.history['loss'], label='Entrenamiento')
plt.plot(history_base.history['val_loss'] + history_fine.history['val_loss'], label='Validación')
plt.title('Pérdida del modelo (Entrenamiento + Fine-Tuning)')
plt.xlabel('Épocas')
plt.ylabel('Loss')
plt.legend()
plt.show()

plt.figure(figsize=(8, 5))
plt.plot(history_base.history['accuracy'] + history_fine.history['accuracy'], label='Entrenamiento')
plt.plot(history_base.history['val_accuracy'] + history_fine.history['val_accuracy'], label='Validación')
plt.title('Precisión del modelo (Entrenamiento + Fine-Tuning)')
plt.xlabel('Épocas')
plt.ylabel('Accuracy')
plt.legend()
plt.show()
