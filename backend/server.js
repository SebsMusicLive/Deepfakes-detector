// server.js
const express = require("express");
const cors = require("cors");
const multer = require("multer");
const fs = require("fs");
const FormData = require("form-data");
require("dotenv").config();

const app = express();
app.use(cors());
app.use(express.json());

const PORT = 5000;

// 🔹 Configurar almacenamiento temporal de archivos
const upload = multer({ dest: "uploads/" });

// 🔹 Ruta de login
app.post("/login", (req, res) => {
  const { username, password } = req.body;
  if (username === "admin" && password === "1234") {
    return res.json({ success: true, message: "Inicio de sesión exitoso" });
  } else {
    return res
      .status(401)
      .json({ success: false, message: "Credenciales incorrectas" });
  }
});

// 🔹 Ruta de análisis con TheHive.ai (API v3)
app.post("/api/deepfake-check", upload.single("file"), async (req, res) => {
  const filePath = req.file?.path;

  try {
    if (!req.file) {
      return res.status(400).json({ error: "No se subió ningún archivo" });
    }

    const accessKey = process.env.THEHIVE_ACCESS_KEY;
    const secretKey = process.env.THEHIVE_SECRET_KEY;

    if (!accessKey || !secretKey) {
      console.error("⚠️ Faltan claves de TheHive en el archivo .env");
      return res
        .status(500)
        .json({ error: "Faltan credenciales de TheHive en el servidor" });
    }

    // Crear form-data con el archivo
    const form = new FormData();
    form.append("media", fs.createReadStream(filePath));

    // 🔹 Enviar solicitud a TheHive API
    const response = await fetch("https://api.thehive.ai/api/v3/task", {
      method: "POST",
      headers: {
        "accept": "application/json",
        "hive-access-key": accessKey,
        "hive-secret-key": secretKey,
      },
      body: form,
    });

    // 🔸 Leer la respuesta en texto (por si no es JSON)
    const text = await response.text();

    let data;
    try {
      data = text ? JSON.parse(text) : null;
    } catch (parseError) {
      console.error("⚠️ Error al parsear respuesta de TheHive:", parseError);
      data = null;
    }

    // 🔸 Si la API devolvió error HTTP
    if (!response.ok) {
      console.error("❌ Error de TheHive API:", response.status, text);
      return res.status(response.status).json({
        error: "TheHive API error",
        status: response.status,
        details: text || "Respuesta vacía o no válida desde TheHive.",
      });
    }

    // 🔸 Si no hay datos válidos
    if (!data) {
      console.error("⚠️ TheHive devolvió una respuesta vacía.");
      return res
        .status(500)
        .json({ error: "Respuesta vacía o no JSON desde TheHive." });
    }

    // ✅ Respuesta correcta
    return res.json(data);
  } catch (error) {
    console.error("💥 Error al llamar a TheHive API:", error);
    return res.status(500).json({ error: "Error al procesar la solicitud." });
  } finally {
    // 🔸 Eliminar archivo temporal de forma segura
    if (filePath && fs.existsSync(filePath)) {
      fs.unlink(filePath, (err) => {
        if (err) console.error("Error al eliminar archivo temporal:", err);
      });
    }
  }
});

app.listen(PORT, () => {
  console.log(`✅ Servidor corriendo en http://localhost:${PORT}`);
});
