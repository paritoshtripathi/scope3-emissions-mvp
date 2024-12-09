const express = require("express");
const app = express();

app.get("/", (req, res) => res.send("Scope 3 Backend API is running!"));

app.listen(3000, () => console.log("Backend running on port 3000"));
