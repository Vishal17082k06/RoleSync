from .connection import db
scores = db.scores

def insert_score(doc):
    doc.setdefault("created_at", __import__("datetime").datetime.utcnow())
    res = scores.insert_one(doc)
    doc["_id"] = str(res.inserted_id)
    return doc
