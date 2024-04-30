from enum import StrEnum
from typing import Optional
from pydantic import BaseModel, Field


class Role(StrEnum):
    admin = "Admin"
    operator = "Operator"


class CloudConnection(BaseModel):
    token: str
    workspace: str
    cloud_url: str = Field(None, alias="cloudUrl")


class Auth(BaseModel):
    username: str
    role: Role
    connection: Optional[CloudConnection]
    
    @property
    def token(self) -> str:
        return self.connection.token if self.connection else ""

    @token.setter
    def token(self, value: str):
        if self.connection is not None:
            self.connection.token = value

    @property
    def is_connected(self) -> bool:
        return True if self.connection else False
