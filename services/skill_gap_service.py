from collections import Counter

from services.ats_service import extract_skills


def build_skill_gap(applications, user_skills="", resume_texts=None):
    resume_texts = resume_texts or []
    demand = Counter()
    for application in applications:
        demand.update(extract_skills(application.job_description))
    existing = set(extract_skills(user_skills))
    for text in resume_texts:
        existing.update(extract_skills(text))
    requested = set(demand)
    missing = requested - existing
    coverage = round(len(requested & existing) / len(requested) * 100, 1) if requested else 0.0
    ordered_demand = [{"skill": skill, "count": count} for skill, count in demand.most_common()]
    recommendations = [
        f"Prioritize {item['skill']}—it appears in {item['count']} tracked job description(s)."
        for item in ordered_demand if item["skill"] in missing
    ][:5]
    if not recommendations and requested:
        recommendations = ["Keep validating your existing skills through projects and quantifiable resume bullets."]
    return {
        "demand": ordered_demand, "existing": sorted(existing), "missing": sorted(missing),
        "coverage": coverage, "recommendations": recommendations,
    }
