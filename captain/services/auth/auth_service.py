import logging
import os
import json
from typing import Optional
import bcrypt
import base64
from captain.types.auth import Auth


def compare_pass(hashed_token: str, plain_token: str):
    logging.info(f"Comparing token: {hashed_token} with {plain_token}")
    ok = bcrypt.checkpw(
        plain_token.encode("utf-8"), hashed_token.encode("utf-8")
    )
    logging.info(f"Token comparison: {ok}")
    return ok


def has_cloud_access(username: str, plain_token: str) -> bool:
    logging.info(f"Checking if {username} has access to the cloud, token: {plain_token}")
    user = get_user(username, plain_token)
    if not user or not user.is_connected:
        return False
    return True


def has_write_access(username: str, plain_token: str) -> bool:
    user = get_user(username, plain_token)
    if not user or user.role == "Operator":
        return False
    return True


def get_user(username: str, plain_token: str) -> Optional[Auth]:
    """ Get the current user if it exists in the local db """
    db_path = os.environ.get("LOCAL_DB_PATH", None)
    logging.info("db_path: ", db_path)

    if not db_path or not os.path.exists(db_path):
        logging.error("Local db not found")
        return None

    with open(db_path, "r") as f:
        logging.info("Reading local db")
        config = json.load(f)
        user = config.get("user", None)
        logging.info("User found: ", user)
        user = Auth(**user)
        logging.info("User: ", user)
        if not compare_pass(user.token, plain_token):
            return None
        if user and user.username == username:
            user.token = plain_token
            return user
    logging.info("User not found")
    return None


def save_user(user: Auth) -> bool:
    """ Save user to local db, return True if successful """
    db_path = os.environ.get("LOCAL_DB_PATH", None)
    if not db_path:
        return False

    config = {}
    if os.path.exists(db_path):
        with open(db_path, "r") as f:
            config = json.load(f)

    with open(db_path, "w") as f:
        # Encrypt the token
        config["user"] = user.model_dump()
        config['user']['token'] = bcrypt.hashpw(user.token.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        json.dump(config, f)
        return True


def get_base64_credentials(username: str, workspace_token: str):
    return base64.b64encode(f"{username}:{workspace_token}".encode("utf-8")).decode("utf-8")
