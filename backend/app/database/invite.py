from ..database.connection import db
from bson import ObjectId
import datetime
import secrets

invites = db.invites

class InviteDB:
    @staticmethod
    def create_invite(candidate_temp_id, email, job_role_id):
        token = secrets.token_urlsafe(32)

        doc = {
            "candidate_temp_id": candidate_temp_id,
            "email": email,
            "job_role_id": job_role_id,
            "token": token,
            "expires_at": datetime.datetime.utcnow() + datetime.timedelta(days=7),
            "used": False
        }

        res = invites.insert_one(doc)
        doc["_id"] = str(res.inserted_id)
        return doc
    
    @staticmethod
    def get_by_token(token):
        return invites.find_one({"token": token, "used": False})

    @staticmethod
    def mark_used(token):
        invites.update_one({"token": token}, {"$set": {"used": True}})
