from fastapi import (
    Depends,
    HTTPException,
    status
)
from fastapi.security import APIKeyCookie
from konoha.core import config
import jwt

cookie_sec = APIKeyCookie(name="session", auto_error=False)


def get_current_user(session: str = Depends(cookie_sec)):
    try:
        payload = jwt.decode(session, config.session_key)
        return payload
    except Exception:
        return None


db = {}


def set_data(key, payload):
    global db
    db[key] = payload


def get_data(key):
    global db
    print(db)
    return db.get(key)
