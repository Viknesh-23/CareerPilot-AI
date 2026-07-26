def calculate_readiness(ats_score, skill_coverage, interview_preparation, profile_completion):
    components = {
        "ats_match": max(0, min(100, float(ats_score or 0))),
        "skill_coverage": max(0, min(100, float(skill_coverage or 0))),
        "interview_preparation": max(0, min(100, float(interview_preparation or 0))),
        "profile_completion": max(0, min(100, float(profile_completion or 0))),
    }
    total = (components["ats_match"] * .30 + components["skill_coverage"] * .25 +
             components["interview_preparation"] * .25 + components["profile_completion"] * .20)
    return {"score": round(max(0, min(100, total)), 1), "components": components}
