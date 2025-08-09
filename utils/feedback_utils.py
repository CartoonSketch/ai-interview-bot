# utils/feedback_utils.py

def generate_feedback(user_answers, correct_answers):
    """
    Compares user answers with correct answers and generates feedback.
    
    Args:
        user_answers (list): List of answers provided by the user.
        correct_answers (list): List of model or expected correct answers.

    Returns:
        dict: Dictionary containing score, detailed feedback for each question.
    """
    feedback = []
    score = 0

    for i, (user_answer, correct_answer) in enumerate(zip(user_answers, correct_answers), start=1):
        if user_answer.strip().lower() == correct_answer.strip().lower():
            feedback.append({
                "question_number": i,
                "status": "Correct",
                "user_answer": user_answer,
                "correct_answer": correct_answer
            })
            score += 1
        else:
            feedback.append({
                "question_number": i,
                "status": "Incorrect",
                "user_answer": user_answer,
                "correct_answer": correct_answer
            })

    result = {
        "score": score,
        "total_questions": len(correct_answers),
        "percentage": round((score / len(correct_answers)) * 100, 2),
        "feedback": feedback
    }
    return result


def generate_detailed_feedback(user_answer, correct_answer):
    """
    Gives a qualitative analysis of the answer beyond exact match.

    Args:
        user_answer (str): User's answer.
        correct_answer (str): Model or expected answer.

    Returns:
        str: Detailed feedback message.
    """
    # This is a simple placeholder; can be replaced with NLP similarity analysis
    if user_answer.strip().lower() == correct_answer.strip().lower():
        return "Excellent! Your answer is spot-on."
    elif correct_answer.lower() in user_answer.lower():
        return "Good! You mentioned key points, but you could be more precise."
    else:
        return "You missed the main points. Please review the topic."
