"""Optional Gemini integration with useful deterministic local fallbacks."""
import json
import os


def _local_questions(role, missing_skills):
    focus = ", ".join(missing_skills[:3]) or "the core skills in this role"
    technical = [
        f"How would you design a reliable solution for a typical {role} problem?",
        f"Explain a challenging technical trade-off you made using {focus}.",
        f"How do you test and monitor the systems you build?",
        f"Walk through how you would debug a production issue relevant to {role}.",
        f"Which fundamentals matter most for a {role}, and why?",
    ]
    hr = ["Tell me about yourself.", "Why are you interested in this role?", "What kind of team helps you do your best work?", "How do you respond to constructive feedback?", "What are your career goals for the next two years?"]
    behavioral = [
        "Tell me about a time you solved an ambiguous problem using the STAR method.",
        "Describe a time you disagreed with a teammate and what happened.",
        "Share an example of a project setback and how you recovered.",
        "Tell me about a time you took ownership beyond your assigned work.",
        "Describe a situation where you had to learn something quickly.",
    ]
    jd = [
        f"How would you apply {skill} in this {role} role?" for skill in (missing_skills + ["the role requirements"] * 5)[:5]
    ]
    return {"Technical": technical, "HR": hr, "Behavioral": behavioral, "JD Specific": jd}


def generate_questions(role, job_description, missing_skills):
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = ("Return valid JSON only with keys Technical, HR, Behavioral, JD Specific. "
                      "Each must contain exactly five concise interview questions. "
                      f"Role: {role}. Job description: {job_description[:4000]}. Missing skills: {missing_skills}.")
            result = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            data = json.loads(result.text.strip().removeprefix("```json").removesuffix("```").strip())
            if all(len(data.get(key, [])) >= 5 for key in ("Technical", "HR", "Behavioral", "JD Specific")):
                return {key: data[key][:5] for key in data if key in {"Technical", "HR", "Behavioral", "JD Specific"}}
        except Exception:
            pass
    return _local_questions(role, missing_skills)


def evaluate_answer(question, answer, category="Technical"):
    text = (answer or "").strip()
    if not text:
        return {"score": 0.0, "feedback": "No answer was submitted. Give a concise, concrete response next time.", "strengths": [], "improvements": ["Answer the question directly."], "suggested_answer": "Start with your approach, add a concrete example, and finish with the result."}
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = ("Return JSON only with score (0-100), feedback, strengths (array), improvements (array), suggested_answer. "
                      f"Evaluate this {category} interview question: {question}\nAnswer: {text}")
            result = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            parsed = json.loads(result.text.strip().removeprefix("```json").removesuffix("```").strip())
            parsed["score"] = max(0, min(100, float(parsed.get("score", 0))))
            return parsed
        except Exception:
            pass
    lower = text.lower()
    words = len(text.split())
    score = min(45, words * 0.55)
    strengths, improvements = [], []
    if words >= 60:
        score += 18; strengths.append("The answer has enough detail to assess.")
    else:
        improvements.append("Add a little more context, your actions, and the result.")
    question_terms = {word for word in question.lower().split() if len(word) > 4}
    relevance = sum(term.strip("?.!,") in lower for term in question_terms)
    score += min(17, relevance * 3)
    if relevance:
        strengths.append("The response addresses part of the question directly.")
    else:
        improvements.append("Use the question's key terms and answer its central prompt directly.")
    technical_terms = {"designed", "tested", "implemented", "analysis", "performance", "api", "database", "solution", "metric"}
    if technical_terms & set(lower.split()):
        score += 10; strengths.append("It includes concrete technical or delivery language.")
    if category == "Behavioral":
        if all(token in lower for token in ("situation", "action", "result")):
            score += 10; strengths.append("The answer uses a clear STAR-style structure.")
        else:
            improvements.append("For behavioral questions, structure the response as Situation, Task, Action, Result.")
    score = round(min(100, score), 1)
    feedback = "A solid foundation. " if score >= 60 else "The response is a starting point. "
    feedback += "Make your contribution and outcome more specific."
    return {"score": score, "feedback": feedback, "strengths": strengths, "improvements": improvements or ["Add a measurable outcome."], "suggested_answer": "State the context, explain the actions you personally took, name the tools or decisions involved, and close with a measurable result."}


def career_recommendation(missing_skills):
    if missing_skills:
        return f"Focus your next learning sprint on {', '.join(missing_skills[:3])}. Build one small project that proves each skill."
    return "Your profile is well aligned with your tracked roles. Focus on tailored applications, interview stories, and measurable project outcomes."
