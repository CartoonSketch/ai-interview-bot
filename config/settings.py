# config/settings.py

import os

# -----------------------------
# Project Metadata
# -----------------------------
PROJECT_NAME = "AI Interview Bot"
VERSION = "1.0"
AUTHOR = "Akash Pandit"

# -----------------------------
# File Paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to the questions.json file
QUESTIONS_FILE = os.path.join(BASE_DIR, "config", "questions.json")

# -----------------------------
# NLP & Scoring Settings
# -----------------------------
# Minimum score to mark an answer as acceptable
MIN_SCORE_THRESHOLD = 0.6

# Number of questions to ask per interview session
QUESTIONS_PER_SESSION = 5

# -----------------------------
# Web App Settings
# -----------------------------
# Flask server configuration
HOST = "127.0.0.1"
PORT = 5000
DEBUG = True

# -----------------------------
# Logging Settings
# -----------------------------
LOG_FILE = os.path.join(BASE_DIR, "logs", "app.log")
LOG_LEVEL = "INFO"

# -----------------------------
# Other Configurations
# -----------------------------
# Enable/disable random question order
RANDOMIZE_QUESTIONS = True

# Show feedback immediately after answer
INSTANT_FEEDBACK = True
