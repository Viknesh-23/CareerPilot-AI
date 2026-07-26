import re
from collections import Counter


ALIASES = {
    "js": "javascript", "ts": "typescript", "reactjs": "react", "node": "node.js",
    "nodejs": "node.js", "postgres": "postgresql", "postgresql": "postgresql",
    "ml": "machine learning", "ai": "artificial intelligence", "aws cloud": "aws",
    "gcp": "google cloud", "k8s": "kubernetes", "ci/cd": "ci/cd",
    "restful": "rest api", "restful api": "rest api", "flask framework": "flask",
}

TECHNICAL_SKILLS = {
    "python", "java", "c", "c++", "c#", "javascript", "typescript", "html", "css",
    "react", "angular", "vue", "node.js", "flask", "django", "fastapi", "spring boot",
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle", "firebase",
    "aws", "azure", "google cloud", "docker", "kubernetes", "terraform", "linux", "git",
    "github", "gitlab", "ci/cd", "jenkins", "github actions", "rest api", "graphql",
    "microservices", "machine learning", "deep learning", "artificial intelligence", "nlp",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "tableau", "power bi",
    "excel", "data analysis", "data structures", "algorithms", "oop", "agile", "scrum",
    "figma", "selenium", "pytest", "unit testing", "cybersecurity", "networking",
}
PROFESSIONAL_SKILLS = {
    "communication", "leadership", "teamwork", "problem solving", "analytical thinking",
    "time management", "stakeholder management", "presentation", "collaboration", "mentoring",
}
STOP_WORDS = {"the", "and", "with", "for", "that", "this", "from", "will", "have", "are", "our", "you", "your", "years", "experience", "work", "team", "role", "job", "skills", "using", "required", "preferred", "ability", "strong", "knowledge", "candidate", "position"}


def normalized_text(text):
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9+#./\\s-]", " ", text)
    for alias, canonical in ALIASES.items():
        text = re.sub(rf"(?<!\w){re.escape(alias)}(?!\w)", canonical, text)
    return re.sub(r"\s+", " ", text)


def extract_skills(text):
    normalized = normalized_text(text)
    found = []
    for skill in sorted(TECHNICAL_SKILLS | PROFESSIONAL_SKILLS, key=len, reverse=True):
        if re.search(rf"(?<!\w){re.escape(skill)}(?!\w)", normalized):
            found.append(skill)
    return sorted(set(found))


def extract_keywords(text, limit=15):
    normalized = normalized_text(text)
    words = re.findall(r"[a-z][a-z+#.-]{2,}", normalized)
    counts = Counter(word for word in words if word not in STOP_WORDS)
    skills = extract_skills(text)
    keyword_list = skills + [word for word, _ in counts.most_common(limit * 2) if word not in skills]
    return keyword_list[:limit]


def analyze_resume(resume_text, job_description):
    jd_skills = set(extract_skills(job_description))
    resume_skills = set(extract_skills(resume_text))
    matched = sorted(jd_skills & resume_skills)
    missing = sorted(jd_skills - resume_skills)
    if jd_skills:
        score = round(len(matched) / len(jd_skills) * 100, 1)
    else:
        # Avoid pretending to score a JD with no recognizable requirements.
        score = 0.0
    suggestions = []
    if missing:
        suggestions.append("Add evidence of relevant skills where you genuinely have hands-on experience: " + ", ".join(missing[:5]) + ".")
    if len(resume_text or "") < 700:
        suggestions.append("Expand project and achievement bullets with measurable outcomes and the tools you used.")
    if not matched:
        suggestions.append("Tailor your professional summary to the role and mirror accurate terminology from the job description.")
    if not suggestions:
        suggestions.append("Your resume aligns well; strengthen it further with metrics and role-specific project outcomes.")
    return {
        "score": score, "matched_skills": matched, "missing_skills": missing,
        "keywords": extract_keywords(job_description), "suggestions": suggestions,
        "skill_coverage": score,
    }
