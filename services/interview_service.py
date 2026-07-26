from collections import defaultdict
from datetime import datetime

from services.gemini_service import evaluate_answer, generate_questions


def create_questions(session, role, description, missing_skills, question_model, db):
    generated = generate_questions(role, description, missing_skills)
    position = 1
    for category in ("Technical", "HR", "Behavioral", "JD Specific"):
        for prompt in generated.get(category, [])[:5]:
            db.session.add(question_model(session_id=session.id, category=category, prompt=prompt, position=position))
            position += 1
    db.session.commit()


def score_session(session):
    buckets = defaultdict(list)
    for question in session.questions:
        if question.score is not None:
            buckets[question.category].append(question.score)
    category_scores = {category: round(sum(values) / len(values), 1) if values else 0.0 for category, values in buckets.items()}
    session.technical_score = category_scores.get("Technical", 0.0)
    session.hr_score = category_scores.get("HR", 0.0)
    session.behavioral_score = category_scores.get("Behavioral", 0.0)
    session.jd_score = category_scores.get("JD Specific", 0.0)
    all_scores = [question.score for question in session.questions if question.score is not None]
    session.overall_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0.0
    session.status = "completed"
    session.completed_at = datetime.utcnow()
    return session


def evaluate_question(question, answer):
    return evaluate_answer(question.prompt, answer, question.category)
