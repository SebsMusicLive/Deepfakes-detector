const express = require("express");
const multer = require("multer");
const fs = require("fs");
const FormData = require("form-data");

// ✅ Carga dinámica de node-fetch (para evitar error "fetch is not a function")
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));

const router = express.Router();
const upload = multer({ dest: "uploads/" });

router.post("/analyze", upload.single("file"), async (req, res) => {
  try {
    if (!req.file) {
      console.error("⚠️ No se recibió ningún archivo del frontend");
      return res.status(400).json({ error: "No se subió ninguna imagen" });
    }

    console.log("📸 Archivo recibido por Node:", req.file.path);

    const formData = new FormData();
    formData.append("file", fs.createReadStream(req.file.path));

    const fastapiURL = "http://localhost:8000/predict";
    console.log(`📤 Enviando imagen a FastAPI -> ${fastapiURL}`);

    const response = await fetch(fastapiURL, {
      method: "POST",
      body: formData,
      headers: formData.getHeaders(),
    }).catch((err) => {
      console.error("🚫 Error al conectar con FastAPI:", err);
      throw new Error("No se pudo conectar con FastAPI");
    });

    console.log("📥 FastAPI respondió con status:", response.status);

    const textResponse = await response.text();
    console.log("🧾 Respuesta bruta de FastAPI:", textResponse);

    let result;
    try {
      result = JSON.parse(textResponse);
    } catch (parseErr) {
      console.error("❌ Error al parsear JSON desde FastAPI:", parseErr);
      return res.status(500).json({ error: "Respuesta inválida del modelo Python" });
    }

    console.log("✅ Resultado del análisis:", result);

    fs.unlinkSync(req.file.path);
    res.json(result);

  } catch (error) {
    console.error("💥 Error al analizar la imagen:", error);
    res.status(500).json({ error: "Error interno del servidor" });
  }
});

module.exports = router;
