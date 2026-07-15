# Book Recommendation Chatbot

TensorFlow content-based recommendation engine + Node.js/Express + MySQL backend,
served to an HTML/CSS/JS chatbot frontend, all connected via REST APIs.

## Folder structure

```
book-recommendation-chatbot/
├── ml-model/                    # Python / TensorFlow
│   ├── data/
│   │   └── books.csv            # <-- put the Kaggle CSV here
│   ├── model/                   # created automatically by train_model.py
│   ├── train_model.py           # trains the embedding model
│   ├── app.py                   # Flask REST API that serves recommendations
│   └── requirements.txt
├── backend/                     # Node.js / Express / MySQL
│   ├── config/db.js
│   ├── controllers/recommendationController.js
│   ├── routes/recommendations.js
│   ├── database/schema.sql
│   ├── server.js
│   ├── package.json
│   └── .env
├── frontend/                    # HTML / CSS / JS chatbot UI
│   ├── index.html
│   ├── css/style.css
│   └── js/chatbot.js
└── README.md
```

## 1. Get the dataset (Kaggle)

Download **"7k Books with Metadata"**:
https://www.kaggle.com/datasets/dylanjcastillo/7k-books-with-metadata

Save the CSV as:
```
ml-model/data/books.csv
```

(Any similarly-structured Kaggle book dataset with title/author/genre/description
columns will work — `train_model.py` normalizes common column-name variants.)

## 2. Train the TensorFlow model

```bash
cd ml-model
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
python train_model.py
```

This trains a TF autoencoder on TF-IDF text features (description + genre + author),
saves book embeddings, and prints an accuracy metric (genre-separation proxy) so
you have a real, reproducible number to quote instead of a guessed one.

## 3. Start the Flask ML service (REST API #1)

```bash
python app.py
```
Runs on `http://localhost:5001`. Test it:
```bash
curl http://localhost:5001/health
```

## 4. Set up MySQL

```bash
mysql -u root -p < backend/database/schema.sql
```
Then edit `backend/.env` with your real MySQL password.

## 5. Start the Express backend (REST API #2)

```bash
cd backend
npm install
npm run dev      # or: npm start
```
Runs on `http://localhost:5000` and also serves the frontend at that same URL.

## 6. Open the chatbot

Visit **http://localhost:5000** in your browser (Express serves `frontend/` statically),
or open `frontend/index.html` directly with VS Code's Live Server extension.

Try messages like:
- `recommend books like Dune`
- `recommend fantasy books`
- `I like slow-paced literary fiction about family`

## How the pieces connect

```
Browser (HTML/CSS/JS)
      │  fetch()
      ▼
Express (Node.js, port 5000) ── MySQL (chat history, users, preferences)
      │  axios REST call
      ▼
Flask (Python, port 5001) ── TensorFlow model + embeddings
```

## Notes for your 2-hour build

- If you're short on time, skip retraining and just run `train_model.py` once —
  the saved artifacts in `ml-model/model/` are reused by `app.py` on every restart.
- `metrics.json` (written by `train_model.py`) holds the accuracy number you can
  reference in your resume/README instead of a placeholder "90%".
- The chatbot's intent parser in `recommendationController.js` is intentionally
  simple (keyword-based) so it's easy to extend during a demo.
