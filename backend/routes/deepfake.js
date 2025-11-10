import express from "express";
import multer from "multer";
import fetch from "node-fetch";
import fs from "fs";

const router = express.Router();
const upload = multer({ dest: "uploads/" });

router.post("/analyze", upload.single("file"), async (req, res) => {
  try {
    const fileStream = fs.createReadStream(req.file.path);

    const response = await fetch("http://127.0.0.1:8000/predict", {
      method: "POST",
      body: fileStream,
      headers: {
        "Content-Type": "application/octet-stream",
      },
    });

    const result = await response.json();

    // Eliminar archivo temporal
    fs.unlinkSync(req.file.path);

    res.json(result);
  } catch (error) {
    console.error("Error al analizar la imagen:", error);
    res.status(500).json({ error: "Error interno del servidor" });
  }
});

export default router;
