const express = require("express");
const cors = require("cors");
const path = require("path");
require("dotenv").config();

const recommendationRoutes = require("./routes/recommendations");

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Serve the frontend directly from the backend for a one-command demo
app.use(express.static(path.join(__dirname, "..", "frontend")));

app.use("/api", recommendationRoutes);

app.get("/api/health", (req, res) => {
  res.json({ status: "Backend running" });
});

app.listen(PORT, () => {
  console.log(`Express server running at http://localhost:${PORT}`);
});
