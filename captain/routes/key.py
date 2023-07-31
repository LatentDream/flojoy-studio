from fastapi import APIRouter, HTTPException, Response, status
from flojoy import set_frontier_api_key, get_credentials
from captain.types.key import GetKeyResponse


router = APIRouter(tags=["env"])


@router.post("/env/")
async def set_env_var(data: dict[str, str]):
    apiKey = data["key"]
    apiValue = data["value"]
    set_frontier_api_key(apiKey, apiValue)
    return Response(status_code=200)


@router.get("/env/", response_model=GetKeyResponse)
async def get_env_var():
    env_vars: list[dict[str, str]] | None = get_credentials()
    if env_vars is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No key found!"
        )
    return GetKeyResponse(env_var=env_vars)
