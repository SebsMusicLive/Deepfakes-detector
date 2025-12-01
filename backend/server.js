// ===================================================
// IMPORTS PRINCIPALES
// ===================================================
const express = require("express");
const cors = require("cors");
const multer = require("multer");
const path = require("path");
require("dotenv").config();


const authMiddleware = require("./middleware/authMiddleware");

// ===================================================
// INICIALIZAR EXPRESS
// ===================================================
const app = express();
app.use(cors());
app.use(express.json());

// ===================================================
// RUTAS DE AUTENTICACIÓN
// ===================================================
const authRoutes = require("./routes/auth");
app.use("/api/auth", authRoutes);

// ===================================================
// RUTAS DE ANÁLISIS DE DEEPFAKES
// ===================================================
const deepfakeRoutes = require("./routes/deepfake");
app.use("/api/deepfakes", deepfakeRoutes);



// ===================================================
// CONFIGURACIÓN DE MULTER (para subida de archivos)
// ===================================================
const storage = multer.diskStorage({
  destination: "./uploads",
  filename: (req, file, cb) => {
    cb(null, `${Date.now()}-${file.originalname}`);
  },
});
const upload = multer({ storage });

// ===================================================
// RUTA PARA PROCESAR IMÁGENES CON EL MODELO DEEPFAKE
// ===================================================
app.post(
  "/api/deepfake-detector",
  authMiddleware,
  upload.single("file"),
  async (req, res) => {
    try {
      if (!req.file) {
        return res.status(400).json({ error: "No se subió ninguna imagen" });
      }

      const imagePath = path.join(__dirname, "uploads", req.file.filename);

      // Ejecutar script Python
      const { spawn } = require("child_process");
      const py = spawn("python", ["./deepfake-detector/predict.py", imagePath]);

      let dataString = "";

      py.stdout.on("data", (data) => {
        dataString += data.toString();
      });

      py.stderr.on("data", (data) => {
        console.error("Error del modelo:", data.toString());
      });

      py.on("close", (code) => {
        try {
          const result = JSON.parse(dataString);
          res.json(result);
        } catch (error) {
          console.error("Error procesando respuesta del modelo:", error);
          res.status(500).json({ error: "Error al procesar la imagen" });
        }
      });
    } catch (error) {
      console.error("Error general en /deepfake-detector:", error);
      res.status(500).json({ error: "Error interno del servidor" });
    }
  }
);

// ===================================================
// SERVIR CARPETA DE UPLOADS
// ===================================================
app.use("/uploads", express.static(path.join(__dirname, "uploads")));

// ===================================================
// INICIAR SERVIDOR
// ===================================================
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`🚀 Servidor corriendo en puerto ${PORT}`));
