const jwt = require("jsonwebtoken");

module.exports = function (req, res, next) {
  const token = req.headers.authorization?.split(" ")[1];
  if (!token) {
    return res.status(403).json({ message: "Token no proporcionado" });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET || "secretkey");
    req.user = decoded;
    next();
  } catch (err) {
    res.status(401).json({ message: "Token inválido o expirado" });
  }
};
