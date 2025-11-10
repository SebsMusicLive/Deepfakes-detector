const express = require("express");
const cors = require("cors");
const dotenv = require("dotenv");
const path = require("path");

// Cargar variables de entorno
dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// 🔹 Middlewares globales
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 🔹 Rutas importadas
const uploadRoutes = require("./routes/upload");
const authRoutes = require("./routes/auth");

// 🔹 Usar rutas
app.use("/api/auth", authRoutes);
app.use("/api/upload", uploadRoutes);

// 🔹 Servir archivos estáticos (opcional, útil para ver las imágenes cargadas)
app.use("/uploads", express.static(path.join(__dirname, "uploads")));

// 🔹 Ruta raíz
app.get("/", (req, res) => {
  res.send("✅ Servidor de DeepFake Detector corriendo correctamente");
});

// 🔹 Manejo de errores global
app.use((err, req, res, next) => {
  console.error("💥 Error global:", err.stack);
  res.status(500).json({ error: "Error interno del servidor" });
});

// 🔹 Iniciar servidor
app.listen(PORT, () => {
  console.log(`🚀 Servidor corriendo en http://localhost:${PORT}`);
});
