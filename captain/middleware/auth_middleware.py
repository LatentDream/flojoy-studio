from typing import Callable, Optional
from fastapi import Request, HTTPException, status
import base64
from captain.services.auth.auth_service import get_user, has_cloud_access, has_write_access
from captain.types.auth import Auth


def _with_verify_access(func: Callable[[str, str]]):
    async def wrapper(req: Request):
        exception_txt = "You are not authorized to perform this action"
        studio_cookie = req.cookies.get("studio-auth")

        if not studio_cookie:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=exception_txt,
            )

        try:
            credentials = base64.b64decode(studio_cookie).decode("utf-8")
            username, token = credentials.split(":", 1)
            authorized = has_cloud_access(username, token)
            func(username, token)

            if not authorized:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=exception_txt,
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=exception_txt,
            )
    return wrapper


@_with_verify_access
async def can_write(username, token):
    """
    Middleware to check if the user can modify protected resources
    Example of use
    @router.get("/write", dependencies=[Depends(can_write)])
    async def update():
        return "resource updated"
    """
    return has_write_access(username, token)


@_with_verify_access
async def is_connected(username, token):
    """
    Middleware to check if the user has access to the cloud
    Example of use
    @router.get("/write", dependencies=[Depends(is_connected)])
    async def update():
        return "resource updated"
    """
    return has_cloud_access(username, token)


def retreive_user(req: Request) -> Auth:
    """
    Access the information store in the current user
    Should be use in tendem with the `dependencies=[Depends(is_connected)]` middleware
    - Raise an HTTPException if the user is not connected
    """
    studio_cookie = req.cookies.get("studio-auth")
    if not studio_cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not connected"
        )
    credentials = base64.b64decode(studio_cookie).decode("utf-8")
    username, token = credentials.split(":", 1)
    user = get_user(username, token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
