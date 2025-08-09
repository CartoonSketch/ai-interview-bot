import os
import json
import random
import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from difflib import SequenceMatcher
from pathlib import Path

# ----------------------------
# Configuration
# ----------------------------
APP_ROOT = Path(__file__).parent
QUESTIONS_FILE = APP_ROOT / "config" / "questions.json"
REPORTS_DIR = APP_ROOT / "data" / "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "replace_this_with_a_random_secret_in_production"  # change before publishing!

# ----------------------------
# Helpers: load questions
# ----------------------------
def load_all_questions():
    if not QUESTIONS_FILE.exists():
        raise FileNotFoundError(f"Questions file not found at {QUESTIONS_FILE}")
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Expecting dict with categories like 'student' and 'hr'
    return data

# ----------------------------
# Helpers: scoring logic
# ----------------------------
def normalize_text(t: str) -> str:
    if not t:
        return ""
    return t.lower().strip()

def keyword_score(answer_text: str, keywords: list) -> float:
    """
    Simple proportion of keywords present in candidate's answer.
    Returns value between 0 and 1.
    """
    if not keywords:
        return 0.0
    ans = normalize_text(answer_text)
    found = 0
    for kw in keywords:
        if kw.lower() in ans:
            found += 1
    return found / len(keywords)

def similarity_score(answer_text: str, ideal_answer: str) -> float:
    """
    Very lightweight semantic proxy using sequence similarity.
    Use sentence-transformers later for better results.
    """
    a = normalize_text(answer_text)
    b = normalize_text(ideal_answer or "")
    if not a or not b:
        return 0.0
    # SequenceMatcher yields ratio between 0 and 1
    return SequenceMatcher(None, a, b).ratio()

def compute_question_score(answer_text: str, question_obj: dict) -> dict:
    """
    Combine keyword and similarity scores into a single score (0-10).
    Returns dict with components for debugging & feedback.
    """
    keywords = question_obj.get("keywords", [])
    ideal_answer = question_obj.get("answer", "")

    kscore = keyword_score(answer_text, keywords)
    sscore = similarity_score(answer_text, ideal_answer)

    # weights - you can tune these
    KW_WEIGHT = 0.6
    SIM_WEIGHT = 0.4

    combined = KW_WEIGHT * kscore + SIM_WEIGHT * sscore
    numeric = round(combined * 10, 2)  # score out of 10

    # Basic feedback pieces
    feedback_notes = []
    if kscore == 0:
        feedback_notes.append("Keywords not detected. Try to mention core concepts.")
    elif kscore < 0.5:
        feedback_notes.append("Partial keywords detected. Add the missing terms.")
    else:
        feedback_notes.append("You mentioned relevant keywords.")

    if sscore > 0.6:
        feedback_notes.append("Answer is close to an ideal response.")
    elif sscore > 0.3:
        feedback_notes.append("Answer has some relevant points but needs clarity.")
    else:
        feedback_notes.append("Answer lacks similarity to the expected response. Explain concepts in a structured manner.")

    return {
        "score_out_of_10": numeric,
        "keyword_score": round(kscore, 3),
        "similarity_score": round(sscore, 3),
        "feedback_notes": feedback_notes
    }

# ----------------------------
# Question selection
# ----------------------------
def pick_questions(category: str, difficulty: str, num_questions: int = 5):
    all_q = load_all_questions()
    category_key = category.lower()
    if category_key not in all_q:
        raise ValueError(f"Unknown category: {category}")
    pool = [q for q in all_q[category_key] if q.get("level","").lower() == difficulty.lower()]
    if not pool:
        # fallback: take any difficulty in the category
        pool = all_q[category_key]
    # random sample or repeat if not enough
    if len(pool) >= num_questions:
        return random.sample(pool, num_questions)
    else:
        # allow repeats to fill slots
        selected = pool.copy()
        while len(selected) < num_questions:
            selected.append(random.choice(pool))
        return selected

# ----------------------------
# Routes: UI pages
# ----------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/mode", methods=["GET", "POST"])
def mode_select():
    """
    POST expected to include 'category' (Student or HR) or GET to show selection page.
    """
    if request.method == "POST":
        category = request.form.get("category", "student")
        session['category'] = category
        return redirect(url_for("io_mode"))
    return render_template("mode.html")

@app.route("/io_mode", methods=["GET", "POST"])
def io_mode():
    """
    Choose between voice or text mode.
    """
    if 'category' not in session:
        return redirect(url_for('index'))
    if request.method == "POST":
        io_mode = request.form.get("io_mode", "text")  # 'voice' or 'text'
        session['io_mode'] = io_mode
        return redirect(url_for("difficulty"))
    return render_template("mode.html")  # you may reuse mode.html or create io-specific template

@app.route("/difficulty", methods=["GET", "POST"])
def difficulty():
    if 'category' not in session:
        return redirect(url_for('index'))
    if request.method == "POST":
        difficulty = request.form.get("difficulty", "easy")
        session['difficulty'] = difficulty
        # optionally number of questions
        num_q = int(request.form.get("num_questions", 5))
        session['num_questions'] = num_q
        return redirect(url_for("interview"))
    # render difficulty selection UI
    return render_template("difficulty.html")

@app.route("/interview")
def interview():
    # Ensure category/difficulty set
    if 'category' not in session or 'difficulty' not in session or 'io_mode' not in session:
        return redirect(url_for('index'))
    return render_template("interview.html")

@app.route("/report")
def report_page():
    if 'report' not in session:
        return redirect(url_for('index'))
    return render_template("report.html", report=session.get('report'))

# ----------------------------
# API endpoints for frontend
# ----------------------------
@app.route("/api/start", methods=["POST"])
def api_start():
    """
    Start interview:
    JSON body: { "category": "student"/"hr", "io_mode": "voice"/"text", "difficulty": "easy"/"medium"/"hard", "num_questions": 5 }
    """
    payload = request.get_json() or {}
    category = payload.get("category") or session.get("category")
    io_mode = payload.get("io_mode") or session.get("io_mode", "text")
    difficulty = payload.get("difficulty") or session.get("difficulty", "easy")
    num_questions = int(payload.get("num_questions", session.get("num_questions", 5)))

    if not category:
        return jsonify({"success": False, "error": "Category not specified"}), 400

    questions = pick_questions(category, difficulty, num_questions)

    # Create interview state in session
    interview_state = {
        "category": category,
        "io_mode": io_mode,
        "difficulty": difficulty,
        "questions": questions,
        "current_index": 0,
        "answers": [],  # list of dicts {question_index, asked_question, given_answer, eval}
        "started_at": datetime.datetime.utcnow().isoformat()
    }
    session['interview_state'] = interview_state
    session.modified = True

    # return first question
    first_q = questions[0]
    return jsonify({
        "success": True,
        "question": {
            "id": 0,
            "text": first_q.get("question"),
            "level": first_q.get("level", difficulty)
        },
        "io_mode": io_mode
    })

@app.route("/api/next_question", methods=["GET"])
def api_next_question():
    """
    Returns next question (without advancing if called multiple times).
    """
    st = session.get('interview_state')
    if not st:
        return jsonify({"success": False, "error": "Interview not started"}), 400
    idx = st.get("current_index", 0)
    questions = st.get("questions", [])
    if idx >= len(questions):
        return jsonify({"success": False, "finished": True}), 200
    q = questions[idx]
    return jsonify({
        "success": True,
        "question": {
            "id": idx,
            "text": q.get("question"),
            "level": q.get("level")
        }
    })

@app.route("/api/submit_answer", methods=["POST"])
def api_submit_answer():
    """
    Submit an answer for current question.
    JSON body: { "answer_text": "..." }
    Returns evaluation and next question (if any).
    """
    payload = request.get_json() or {}
    answer_text = payload.get("answer_text", "")

    st = session.get('interview_state')
    if not st:
        return jsonify({"success": False, "error": "Interview not started"}), 400

    idx = st.get("current_index", 0)
    questions = st.get("questions", [])

    if idx >= len(questions):
        return jsonify({"success": False, "error": "No more questions", "finished": True}), 200

    qobj = questions[idx]
    eval_result = compute_question_score(answer_text, qobj)

    # record answer
    st['answers'].append({
        "question_index": idx,
        "question": qobj.get("question"),
        "given_answer": answer_text,
        "evaluation": eval_result
    })

    # advance pointer
    st['current_index'] = idx + 1
    session['interview_state'] = st
    session.modified = True

    # prepare either next question or finish
    if st['current_index'] >= len(questions):
        # finish - prepare final report
        report = prepare_report(st)
        session['report'] = report
        session.modified = True
        return jsonify({
            "success": True,
            "evaluation": eval_result,
            "finished": True,
            "report": report
        })
    else:
        next_q = questions[st['current_index']]
        return jsonify({
            "success": True,
            "evaluation": eval_result,
            "finished": False,
            "next_question": {
                "id": st['current_index'],
                "text": next_q.get("question"),
                "level": next_q.get("level")
            }
        })

@app.route("/api/get_report", methods=["GET"])
def api_get_report():
    report = session.get('report')
    if not report:
        return jsonify({"success": False, "error": "Report not available"}), 400
    return jsonify({"success": True, "report": report})

# ----------------------------
# Report & feedback generation
# ----------------------------
def prepare_report(interview_state: dict) -> dict:
    answers = interview_state.get("answers", [])
    total_score = 0.0
    max_possible = 10 * len(answers)
    strengths = []
    weaknesses = []
    suggestions = []

    for ans in answers:
        ev = ans.get("evaluation", {})
        sc = ev.get("score_out_of_10", 0)
        total_score += sc
        # derive strengths/weaknesses from feedback_notes
        notes = ev.get("feedback_notes", [])
        # simplistic categorization
        for note in notes:
            if "not detected" in note or "lacks" in note or "needs" in note or "partial" in note:
                weaknesses.append({"question": ans.get("question"), "note": note})
            else:
                strengths.append({"question": ans.get("question"), "note": note})

    avg_score = round(total_score / max(1, len(answers)), 2)

    # generate generic suggestions based on weaknesses
    if weaknesses:
        suggestions.append("Try structuring answers using STAR method (Situation, Task, Action, Result) for HR questions.")
        suggestions.append("Mention core keywords and definitions for technical answers. Briefly give an example or use-case if possible.")
    else:
        suggestions.append("Great job. Continue practicing live mock interviews.")

    report = {
        "category": interview_state.get("category"),
        "difficulty": interview_state.get("difficulty"),
        "started_at": interview_state.get("started_at"),
        "completed_at": datetime.datetime.utcnow().isoformat(),
        "num_questions": len(answers),
        "average_score_out_of_10": avg_score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "detailed_answers": answers
    }

    # save to disk for record (timestamped)
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    fname = REPORTS_DIR / f"report_{timestamp}.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report

# ----------------------------
# Simple utility route: clear session (for dev)
# ----------------------------
@app.route("/reset", methods=["GET"])
def reset_session():
    session.clear()
    return redirect(url_for("index"))

# ----------------------------
# Run the app
# ----------------------------
if __name__ == "__main__":
    # set debug=False for production
    app.run(host="0.0.0.0", port=5000, debug=True)
