# utils/nlp_utils.py

import re
from difflib import SequenceMatcher

def clean_text(text):
    """
    Cleans the input text by:
    - Lowercasing
    - Removing special characters and extra spaces
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def similarity_ratio(a, b):
    """
    Returns similarity ratio between two strings.
    """
    return SequenceMatcher(None, a, b).ratio()


def evaluate_answer(user_answer, correct_keywords):
    """
    Evaluates the candidate's answer based on keyword presence.
    
    :param user_answer: The answer provided by the candidate
    :param correct_keywords: List of important keywords
    :return: score (int), feedback list
    """
    cleaned_answer = clean_text(user_answer)
    score = 0
    feedback = []

    for keyword in correct_keywords:
        if keyword.lower() in cleaned_answer:
            score += 1
        else:
            feedback.append(f"Consider mentioning '{keyword}' in your answer.")

    return score, feedback


def calculate_percentage(score, total):
    """
    Calculates the percentage score.
    """
    if total == 0:
        return 0
    return round((score / total) * 100, 2)


def generate_feedback(all_feedback):
    """
    Combines multiple feedback lists into a single list without duplicates.
    """
    seen = set()
    unique_feedback = []
    for fb in all_feedback:
        if fb not in seen:
            unique_feedback.append(fb)
            seen.add(fb)
    return unique_feedback
