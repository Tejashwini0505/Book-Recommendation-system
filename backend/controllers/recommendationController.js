const axios = require("axios");
const pool = require("../config/db");

const ML_SERVICE_URL = process.env.ML_SERVICE_URL || "http://localhost:5001";

/**
 * Very small intent parser for the chatbot.
 * Recognizes:
 *   "recommend books like <title>"
 *   "recommend <genre> books" / "suggest some <genre> books"
 *   anything else -> treated as a free-text interest query
 */
function parseIntent(message) {
  const text = message.toLowerCase().trim();

  const likeMatch = text.match(/like\s+(.+)/);
  if (likeMatch) {
    return { intent: "by_title", value: likeMatch[1].replace(/[?.!]$/, "").trim() };
  }

  const genreMatch = text.match(/(?:recommend|suggest)\s+(?:some\s+)?([a-z\s]+?)\s+books/);
  if (genreMatch) {
    return { intent: "by_genre", value: genreMatch[1].trim() };
  }

  return { intent: "by_text", value: message };
}

async function handleChat(req, res) {
  const { message, userId } = req.body;

  if (!message || !message.trim()) {
    return res.status(400).json({ error: "message is required" });
  }

  const { intent, value } = parseIntent(message);

  try {
    let mlResponse;
    let botReplyIntro;

    if (intent === "by_title") {
      mlResponse = await axios.post(`${ML_SERVICE_URL}/recommend`, { title: value, top_n: 5 });
      botReplyIntro = `Because you liked "${mlResponse.data.based_on}", you might enjoy:`;
    } else if (intent === "by_genre") {
      mlResponse = await axios.post(`${ML_SERVICE_URL}/recommend_by_genre`, { genre: value, top_n: 5 });
      botReplyIntro = `Here are some top ${value} books:`;
    } else {
      mlResponse = await axios.post(`${ML_SERVICE_URL}/recommend_by_text`, { text: value, top_n: 5 });
      botReplyIntro = `Based on what you're looking for, here are some recommendations:`;
    }

    const recommendations = mlResponse.data.recommendations;
    const botResponse = JSON.stringify({ intro: botReplyIntro, recommendations });

    // Log the conversation to MySQL
    await pool.query(
      "INSERT INTO chat_history (user_id, user_message, bot_response) VALUES (?, ?, ?)",
      [userId || null, message, botResponse]
    );

    return res.json({ intro: botReplyIntro, recommendations });
  } catch (err) {
    if (err.response) {
      // ML service responded with an error (e.g. book not found)
      return res.status(err.response.status).json({ error: err.response.data.error || "Recommendation failed" });
    }
    console.error("Chat handling error:", err.message);
    return res.status(500).json({ error: "Something went wrong generating recommendations" });
  }
}

async function getChatHistory(req, res) {
  const { userId } = req.params;
  try {
    const [rows] = await pool.query(
      "SELECT * FROM chat_history WHERE user_id = ? ORDER BY created_at DESC LIMIT 50",
      [userId]
    );
    res.json(rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Could not fetch chat history" });
  }
}

async function savePreference(req, res) {
  const { userId, genre, likedBookTitle } = req.body;
  try {
    await pool.query(
      "INSERT INTO user_preferences (user_id, preferred_genre, liked_book_title) VALUES (?, ?, ?)",
      [userId, genre || null, likedBookTitle || null]
    );
    res.status(201).json({ message: "Preference saved" });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Could not save preference" });
  }
}

module.exports = { handleChat, getChatHistory, savePreference };
