const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

const USER = {
  username: "admin",
  password: bcrypt.hashSync("1234", 10) // contraseña cifrada
};

exports.loginUser = (req, res) => {
  const { username, password } = req.body;

  if (username !== USER.username) {
    return res.status(401).json({ message: "Usuario no encontrado" });
  }

  const validPassword = bcrypt.compareSync(password, USER.password);
  if (!validPassword) {
    return res.status(401).json({ message: "Contraseña incorrecta" });
  }

  const token = jwt.sign({ username }, process.env.JWT_SECRET || "secretkey", { expiresIn: "1h" });
  res.json({ token });
};
