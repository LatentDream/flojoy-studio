import os
import json
from typing import Optional
import bcrypt
import base64
from captain.types.auth import Auth


def compare_pass(hashed_token: str, plain_token: str):
    return bcrypt.checkpw(
        plain_token.encode("utf-8"), hashed_token.encode("utf-8")
    )


def has_cloud_access(username: str, plain_token: str) -> bool:
    user = get_user(username, plain_token)
    if not user or user == "Local":
        return False
    return True


def has_write_access(username: str, plain_token: str) -> bool:
    user = get_user(username, plain_token)
    if not user or user.permission == "Operator":
        return False
    return True


def get_user(username: str, plain_token: str) -> Optional[Auth]:
    """ Get the current user if it exists in the local db """
    db_path = os.environ.get("LOCAL_DB_PATH", None)

    if not db_path:
        return None

    if not os.path.exists(db_path):
        return None
    with open(db_path, "r") as f:
        config = json.load(f)
        user = config.get("user", None)
        user = Auth(**user)
        if not compare_pass(user.token, plain_token):
            return None
        if user and user.username == username:
            user.token = plain_token
            return user

    return None


def save_user(user: Auth) -> bool:
    """ Save user to local db, return True if successful """
    db_path = os.environ.get("LOCAL_DB_PATH", None)
    if not db_path:
        return False

    if not os.path.exists(db_path):
        open(db_path, "x").close()

    with open(db_path, "rw") as f:
        config = json.load(f)
        config.user = user
        json.dump(config, f)
        return True


def get_base64_credentials(username: str, workspace_token: str):
    return base64.b64encode(f"{username}:{workspace_token}".encode("utf-8")).decode("utf-8")
