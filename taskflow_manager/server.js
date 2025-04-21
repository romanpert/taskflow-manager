const express = require('express');
const path = require('path');

const app = express();
const PORT = 2411; // Cambiaste el puerto

// Servir archivos estáticos (CSS, JS, imágenes)
app.use('/assets', express.static(path.join(__dirname, 'frontend/assets')));

// Servir el HTML principal en la raíz "/"
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'frontend', 'taskflow.html'));
});

app.listen(PORT, () => {
  console.log(`TaskFlow web server listening on http://localhost:${PORT}`);
});
