const jwt = require('jsonwebtoken');

function authMiddleware(req, res, next) {
  const token = req.header('Authorization')?.split(' ')[1];
  if (!token) return res.status(403).json({ message: 'Token requerido' });

  try {
    const verified = jwt.verify(token, process.env.JWT_SECRET || "secretkey");
    req.user = verified;
    next();
  } catch (err) {
    res.status(401).json({ message: 'Token inválido' });
  }
}

module.exports = authMiddleware;
