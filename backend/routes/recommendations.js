const express = require("express");
const router = express.Router();
const { handleChat, getChatHistory, savePreference } = require("../controllers/recommendationController");
const pool = require("../config/db");

// Chatbot endpoint - the frontend calls this
router.post("/chat", handleChat);

// Chat history for a given user
router.get("/history/:userId", getChatHistory);

// Save an explicit user preference
router.post("/preferences", savePreference);

// Simple user creation/lookup (kept minimal for the demo)
router.post("/users", async (req, res) => {
  const { username } = req.body;
  if (!username) return res.status(400).json({ error: "username is required" });

  try {
    await pool.query("INSERT IGNORE INTO users (username) VALUES (?)", [username]);
    const [rows] = await pool.query("SELECT * FROM users WHERE username = ?", [username]);
    res.json(rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Could not create/find user" });
  }
});

module.exports = router;
