const express = require('express');
const path = require('path');

const app = express();
const PORT = 3000;  // puerto para servir la web

// servir archivos estáticos de la carpeta frontend
app.use('/', express.static(path.join(__dirname, 'frontend')));

app.listen(PORT, () => {
  console.log(`TaskFlow web server listening on http://localhost:${PORT}`);
});
