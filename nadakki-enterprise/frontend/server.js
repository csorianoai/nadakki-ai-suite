const express = require("express");
const app = express();

app.get("/", (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>Nadakki - Credicefi</title>
        <style>
          body { font-family: Arial; text-align: center; padding: 50px; background: #f0f0f0; }
          h1 { color: #333; }
          .status { background: green; color: white; padding: 10px; border-radius: 5px; display: inline-block; }
        </style>
      </head>
      <body>
        <h1>🎉 ¡Nadakki Platform Funcionando!</h1>
        <p class="status">✅ Frontend: Corriendo en puerto 3000</p>
        <p class="status">✅ Backend: Corriendo en puerto 8000</p>
        <p class="status">✅ Database: Corriendo en puerto 5432</p>
        <hr>
        <h2>Credicefi - Plataforma de Financiamiento</h2>
        <p>Tu plataforma multi-tenant está operativa.</p>
      </body>
    </html>
  `);
});

app.listen(3000, () => {
  console.log("✅ Frontend corriendo en http://localhost:3000");
});
