exports.handleFileUpload = (req, res) => {
  if (!req.file) return res.status(400).json({ message: "No se subió ningún archivo" });

  res.json({
    message: "Archivo subido correctamente",
    filename: req.file.filename,
    url: `/uploads/${req.file.filename}`
  });
};
