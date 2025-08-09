# AI Interview Bot 🤖

An AI-powered interview simulation tool that asks technical and HR questions, evaluates responses, and provides feedback — all through voice or text interaction.

## 📌 Features
- **Voice & Text Input** — Users can answer interview questions by speaking or typing.
- **AI Question Bank** — Predefined HR & technical questions stored in `questions.json`.
- **NLP Evaluation** — Uses AI to evaluate answers and give a score/feedback.
- **Speech Output** — Bot speaks questions using Google Text-to-Speech (gTTS).
- **Web Interface** — Built with Flask for easy access in the browser.

## 🚀 Installation

### 1️⃣ Clone the repository

- git clone https://github.com/your-username/ai-interview-bot.git
cd ai-interview-bot

### 2️⃣ Create and activate virtual environment

python -m venv venv
source venv/bin/activate   # For Linux/Mac
venv\Scripts\activate      # For Windows

### 3️⃣ Install dependencies

- pip install -r requirements.txt

### ▶️ Run the Application

- python app.py

The app will be available at http://127.0.0.1:5000/.

## 🛠 Technologies Used

- Python 3.10+

- Flask — Web framework

- SpeechRecognition — Speech-to-Text

- gTTS — Text-to-Speech

- Transformers + Torch — NLP evaluation

- scikit-learn — Similarity scoring

- HTML/CSS/JS — Frontend

## 📜 Example Question Categories

- HR Questions

"Tell me about yourself."

"Why should we hire you?"


- Technical Questions

"What is polymorphism in OOP?"

"Explain overfitting in machine learning."

## 📌 Future Enhancements

- Add camera-based body language analysis.

- Add multilingual support.

- Store interview results in a database.

## 🤝 Contributing

Pull requests are welcome! Please open an issue first to discuss any major changes.


## 📄 License

This project is licensed under the MIT License.

If you want, I can now prepare the **`questions.json`** so that your bot has an actual question bank ready to go for HR + technical rounds.  
That way, you can immediately start testing the AI bot.

