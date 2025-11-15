from .connection import db
import datetime

job_roles = db.job_roles

class JobRoleDB:
    @staticmethod
    def insert(role_doc):
        role_doc.setdefault("created_at", datetime.datetime.utcnow())
        res = job_roles.insert_one(role_doc)
        role_doc["_id"] = str(res.inserted_id)
        return role_doc

    @staticmethod
    def get(role_id):
        from bson.objectid import ObjectId
        return job_roles.find_one({"_id": ObjectId(role_id)})
