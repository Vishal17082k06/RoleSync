from .connection import db
from bson.objectid import ObjectId
import datetime
from typing import Optional

users_col = db.users

def create_user_doc(email: str, hashed_password: str, role: str, name: Optional[str]=None, linked_id: Optional[str]=None):
    doc = {
        "email": email.lower(),
        "hashed_password": hashed_password,
        "role": role,
        "name": name,
        "linked_id": linked_id,
        "created_at": datetime.datetime.utcnow()
    }
    res = users_col.insert_one(doc)
    doc["_id"] = str(res.inserted_id)
    return doc

def get_user_by_email(email: str):
    r = users_col.find_one({"email": email.lower()})
    if not r:
        return None
    r["_id"] = str(r["_id"])
    return r

def get_user_by_id(user_id: str):
    try:
        r = users_col.find_one({"_id": ObjectId(user_id)})
        if not r:
            return None
        r["_id"] = str(r["_id"])
        return r
    except Exception:
        return None

def link_user_to_profile(user_id: str, linked_id: str):
    from bson.objectid import ObjectId
    users_col.update_one({"_id": ObjectId(user_id)}, {"$set": {"linked_id": linked_id}})
    return get_user_by_id(user_id)
