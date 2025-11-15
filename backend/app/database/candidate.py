from .connection import db
from bson.objectid import ObjectId
import datetime

candidates_col = db.candidates

class CandidateDB:

    def insert_candidate_doc(doc):
        doc.setdefault("created_at", datetime.datetime.utcnow())
        doc.setdefault("updated_at", datetime.datetime.utcnow())
        res = candidates_col.insert_one(doc)
        doc["_id"] = str(res.inserted_id)
        return doc

    # ---------------------------------------------------------
    # 2. Find by resume hash (duplicate detection)
    # ---------------------------------------------------------
    @staticmethod
    def find_by_hash(h):
        r = candidates_col.find_one({"file_hash": h})
        if not r:
            return None
        r["_id"] = str(r["_id"])
        return r

    # ---------------------------------------------------------
    # 3. Find by email (auto-linking)
    # ---------------------------------------------------------
    @staticmethod
    def find_by_email(email: str):
        r = candidates_col.find_one({"email": email.lower()})
        if not r:
            return None
        r["_id"] = str(r["_id"])
        return r

    # ---------------------------------------------------------
    # 4. Save resume parsing details
    # ---------------------------------------------------------
    @staticmethod
    def update_parsed_resume(candidate_id, parsed_data: dict):
        candidates_col.update_one(
            {"_id": ObjectId(candidate_id)},
            {"$set": {
                "name": parsed_data.get("name"),
                "email": parsed_data.get("email", "").lower(),
                "skills": parsed_data.get("skills", []),
                "projects": parsed_data.get("projects", []),
                "education": parsed_data.get("education", []),
                "experience_years": parsed_data.get("experience_years", 0),
                "parsed_text": parsed_data.get("raw_text", ""),
                "updated_at": datetime.datetime.utcnow()
            }}
        )
        return CandidateDB.get(candidate_id)

    # ---------------------------------------------------------
    # 5. Store analysis for a specific JD (match_score, ats_score)
    # ---------------------------------------------------------
    @staticmethod
    def add_analysis(candidate_id, job_role_id, analysis_dict):
        """
        analysis_dict example:
        {
            "job_role_id": "...",
            "match_score": 78,
            "ats_score": 62,
            "skill_gaps": [...],
            "project_relevance": 0.63,
            "fit_reasoning": "...",
            "learning_path": {...},
            "timestamp": datetime.utcnow()
        }
        """

        analysis_dict.setdefault("timestamp", datetime.datetime.utcnow())

        candidates_col.update_one(
            {"_id": ObjectId(candidate_id)},
            {"$push": {"analysis": analysis_dict},
             "$set": {"updated_at": datetime.datetime.utcnow()}}
        )
        return True

    # ---------------------------------------------------------
    # 6. Get top N candidates for a job role (ranking)
    # ---------------------------------------------------------
    @staticmethod
    def get_top_n(job_role_id, n=5):
        cursor = candidates_col.find(
            {"analysis.job_role_id": job_role_id},
            {"analysis": 1}
        )

        ranking = []
        for r in cursor:
            analyses = r.get("analysis", [])
            entry = next((a for a in analyses if a.get("job_role_id") == job_role_id), None)
            if entry:
                ranking.append({
                    "candidate_id": str(r["_id"]),
                    "match_score": entry.get("match_score", 0),
                    "ats_score": entry.get("ats_score", 0),
                })

        ranked = sorted(ranking, key=lambda x: (x["match_score"], x["ats_score"]), reverse=True)
        return ranked[:n]

    # ---------------------------------------------------------
    # 7. Store recruiter feedback for rejection/shortlist
    # ---------------------------------------------------------
    @staticmethod
    def add_feedback(candidate_id, job_role_id, recruiter_id, feedback_text):
        fb = {
            "job_role_id": job_role_id,
            "recruiter_id": recruiter_id,
            "feedback": feedback_text,
            "timestamp": datetime.datetime.utcnow()
        }
        return candidates_col.update_one(
            {"_id": ObjectId(candidate_id)},
            {"$push": {"feedback_history": fb}}
        )

    # ---------------------------------------------------------
    # 8. Store resume submission history
    # ---------------------------------------------------------
    @staticmethod
    def add_submission(candidate_id, job_role_id, recruiter_id):
        record = {
            "job_role_id": job_role_id,
            "recruiter_id": recruiter_id,
            "timestamp": datetime.datetime.utcnow()
        }
        candidates_col.update_one(
            {"_id": ObjectId(candidate_id)},
            {"$push": {"submission_history": record}}
        )

    # ---------------------------------------------------------
    # 9. General getter
    # ---------------------------------------------------------
    @staticmethod
    def get(candidate_id):
        try:
            r = candidates_col.find_one({"_id": ObjectId(candidate_id)})
            if not r:
                return None
            r["_id"] = str(r["_id"])
            return r
        except:
            return None

    # ---------------------------------------------------------
    # 10. For LLM training samples (optional)
    # ---------------------------------------------------------
    @staticmethod
    def find_texts(limit=200):
        cur = candidates_col.find({}, {"_id": 1, "parsed_text": 1}).limit(limit)
        return [{"_id": str(r["_id"]), "text": r.get("parsed_text", "")} for r in cur]

    @staticmethod
    def add_feedback(candidate_id, job_role_id, recruiter_id, feedback_text):
        fb = {
            "job_role_id": job_role_id,
            "recruiter_id": recruiter_id,
            "feedback": feedback_text,
            "timestamp": datetime.datetime.utcnow()
        }
        return candidates_col.update_one(
            {"_id": ObjectId(candidate_id)},
            {"$push": {"feedback_history": fb}}
        )
    
    @staticmethod
    def link_resume_to_user(candidate_temp_id, user_id):
        candidates_col.update_one(
            {"_id": ObjectId(candidate_temp_id)},
            {"$set": {"linked_user_id": user_id}}
        )

