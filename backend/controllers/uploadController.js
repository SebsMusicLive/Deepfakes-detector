const fs = require("fs");
const fetch = require("node-fetch");
const path = require("path");

/**
 * Controlador encargado de recibir un archivo del cliente,
 * enviarlo al modelo de FastAPI para análisis, y devolver
 * el resultado de predicción al frontend.
 */
exports.handleFileUpload = async (req, res) => {
  const filePath = req.file?.path;

  try {
    if (!req.file) {
      return res.status(400).json({ error: "No se ha subido ningún archivo." });
    }

    // 📤 Enviar imagen al modelo local (FastAPI)
    const fileStream = fs.createReadStream(filePath);

    const response = await fetch("http://127.0.0.1:8000/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/octet-stream",
      },
      body: fileStream,
    });

    // 📥 Leer la respuesta del modelo
    const text = await response.text();

    let data;
    try {
      data = text ? JSON.parse(text) : null;
    } catch (err) {
      console.error("⚠️ Error al parsear la respuesta del modelo:", err);
      data = null;
    }

    // ❌ Si hubo error en FastAPI
    if (!response.ok || !data) {
      console.error("❌ Error desde FastAPI:", text);
      return res.status(500).json({
        error: "Error al comunicarse con el modelo de DeepFake",
        details: text || "Respuesta vacía o inválida desde FastAPI.",
      });
    }

    // ✅ Éxito: devolver resultado al frontend
    return res.json({
      success: true,
      label: data.label,
      confidence: data.confidence,
      analyzedBy: req.user?.username || "sistema",
    });
  } catch (error) {
    console.error("💥 Error en el controlador de carga:", error);
    return res.status(500).json({ error: "Error interno al analizar la imagen." });
  } finally {
    // 🧹 Eliminar archivo temporal
    if (filePath && fs.existsSync(filePath)) {
      fs.unlink(filePath, (err) => {
        if (err) console.error("Error al eliminar archivo temporal:", err);
      });
    }
  }
};
