import json
import os

def load_questions(file_path):
    """
    Load interview questions from a JSON file.
    Returns a list of questions.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Questions file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
            if not isinstance(data, list):
                raise ValueError("Questions JSON file must contain a list of questions.")
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON: {e}")

def get_questions_by_difficulty(questions, difficulty):
    """
    Filters questions by difficulty level.
    Difficulty can be: 'easy', 'medium', or 'hard'.
    """
    return [q for q in questions if q.get("difficulty", "").lower() == difficulty.lower()]

def get_questions_by_category(questions, category):
    """
    Filters questions by category (e.g., 'technical', 'hr', 'behavioral').
    """
    return [q for q in questions if q.get("category", "").lower() == category.lower()]

def get_random_questions(questions, limit=5):
    """
    Returns a random selection of questions from the list.
    """
    import random
    return random.sample(questions, min(limit, len(questions)))


# Example usage
if __name__ == "__main__":
    questions_file = os.path.join(os.path.dirname(__file__), "../questions.json")
    all_questions = load_questions(questions_file)

    print(f"Total questions loaded: {len(all_questions)}")
    easy_questions = get_questions_by_difficulty(all_questions, "easy")
    print(f"Easy questions: {len(easy_questions)}")
