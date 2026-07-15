# 📚 Book Recommendation Chatbot

An AI-powered Book Recommendation Chatbot that provides personalized book suggestions using Machine Learning and Natural Language Processing. The system combines a TensorFlow-based recommendation engine with a Node.js backend and MySQL database to deliver real-time recommendations through a user-friendly web interface.

## 🚀 Features

- Personalized book recommendations
- AI-powered recommendation engine using TensorFlow
- REST API integration between ML service and backend
- User preference management
- Chat-style recommendation interface
- MySQL database integration
- Responsive web interface
- Real-time recommendation generation

---

## 🛠️ Tech Stack

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Node.js
- Express.js
- REST APIs

### Machine Learning
- Python
- TensorFlow
- Scikit-Learn
- Flask

### Database
- MySQL

---

## 📂 Project Structure

```text
book-recommendation-chatbot/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── backend/
│   ├── config/
│   ├── controllers/
│   ├── routes/
│   ├── database/
│   │   └── schema.sql
│   ├── .env
│   ├── package.json
│   └── server.js
│
├── ml-model/
│   ├── data/
│   ├── model/
│   ├── train_model.py
│   ├── app.py
│   └── requirements.txt
│
└── README.md
```

---

## 📊 Dataset

Dataset used:

**7K Books with Metadata**

Source:
https://www.kaggle.com/datasets/dylanjcastillo/7k-books-with-metadata

The dataset contains:
- Book titles
- Authors
- Genres
- Ratings
- Descriptions
- Metadata

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/Tejashwini0505/Book-Recommendation-system.git
cd Book-Recommendation-system
```

---

## 🧠 Machine Learning Setup

Navigate to ML folder:

```bash
cd ml-model
```

Create virtual environment:

```bash
py -3.12 -m venv venv
```

Activate environment:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Train model:

```bash
python train_model.py
```

Start Flask API:

```bash
python app.py
```

ML Service runs on:

```text
http://localhost:5001
```

---

## 🗄️ Database Setup

Start MySQL Server.

Create database:

```sql
CREATE DATABASE bookdb;
```

Import schema:

```sql
USE bookdb;
SOURCE schema.sql;
```

Tables:
- users
- books
- user_preferences
- chat_history

---

## 🔧 Backend Setup

Navigate to backend:

```bash
cd backend
```

Install dependencies:

```bash
npm install
```

Configure `.env`

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=bookdb
PORT=5000
```

Run backend:

```bash
node server.js
```

Backend runs on:

```text
http://localhost:5000
```

---

## 🎨 Frontend Setup

Open frontend folder:

```bash
cd frontend
```

Run using VS Code Live Server or open:

```text
index.html
```

---

## 🔄 System Architecture

```text
Frontend (HTML/CSS/JS)
           │
           ▼
Node.js + Express Backend
           │
           ▼
Flask ML API
           │
           ▼
TensorFlow Recommendation Model
           │
           ▼
MySQL Database
```

---

## 📈 Project Highlights

- Trained recommendation engine using 6,000+ book records.
- Built RESTful APIs for recommendation generation.
- Integrated TensorFlow model with Node.js backend.
- Implemented database-driven user preference tracking.
- Developed a responsive chatbot-style user interface.
- Enabled real-time personalized recommendations.

---

## 📸 Future Enhancements

- User authentication and login
- Collaborative filtering
- Deep learning recommendation models
- Book review analysis
- Recommendation history dashboard
- Deployment on AWS/Render

---

## 👩‍💻 Author

**Tejashwini S**

Computer Science Engineering Student

GitHub:
https://github.com/Tejashwini0505

LinkedIn:
(Add your LinkedIn profile URL)

---
