from enum import StrEnum
from pydantic import BaseModel


class Permission(StrEnum):
    admin = "Admin"
    operator = "Operator"
    localUser = "Local"


class Auth(BaseModel):
    username: str
    permission: Permission
    # If connected with cloud
    token: str
    url: str

