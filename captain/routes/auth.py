from fastapi import APIRouter, Response
from captain.services.auth.auth_service import (
    save_user,
    get_base64_credentials,
)
from captain.types.auth import Auth
import logging

router = APIRouter(tags=["auth"])


@router.post("/auth/login/")
async def login(response: Response, auth: Auth):
    """ Login to the backend of the app
    - Actual auth with password and username is done in the frontend with cloud
    - Backend auth serves as a middleware to store Cloud credentials
    """
    logging.info(f"Login attempt for {auth.username} - Connected: {auth.is_connected}")
    save_user(auth)
    encoded_credentials = get_base64_credentials(auth.username, auth.token)
    response.set_cookie(
        key="studio-auth",
        value=encoded_credentials,
        path="/",
        samesite="none",
        secure=True,
    )
    return "Login successful"
