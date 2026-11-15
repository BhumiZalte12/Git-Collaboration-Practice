"""Small in-memory Devices API with JWT-protected write operations."""

from datetime import datetime, timedelta, timezone
import os
from typing import Optional

import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel, Field, field_validator
from starlette.responses import Response


load_dotenv()

TRAINING_USERNAME = os.getenv("NETPULSE_USERNAME", "").strip()
TRAINING_PASSWORD = os.getenv("NETPULSE_PASSWORD", "")
JWT_SECRET = os.getenv("NETPULSE_JWT_SECRET", "")
JWT_ALGORITHM = "HS256"
TOKEN_LIFETIME = timedelta(minutes=30)

if not TRAINING_USERNAME or not TRAINING_PASSWORD:
    raise RuntimeError("Set NETPULSE_USERNAME and NETPULSE_PASSWORD in your local .env file.")
if len(JWT_SECRET) < 32:
    raise RuntimeError("Set NETPULSE_JWT_SECRET to a random value at least 32 characters long.")

password_hasher = PasswordHash.recommended()
TRAINING_PASSWORD_HASH = password_hasher.hash(TRAINING_PASSWORD)

app = FastAPI(
    title="NetPulse Devices API",
    description="Public device reads with JWT-protected device changes.",
    version="1.0.0",
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


class DeviceFields(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    device_type: str = Field(min_length=1, max_length=60)
    status: str = Field(min_length=1, max_length=40)
    location: str = Field(min_length=1, max_length=100)

    @field_validator("name", "device_type", "status", "location", mode="before")
    @classmethod
    def trim_required_text(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("Text fields cannot be blank.")
        return value


class DeviceCreate(DeviceFields):
    pass


class DeviceReplace(DeviceFields):
    pass


class DevicePatch(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    device_type: Optional[str] = Field(default=None, min_length=1, max_length=60)
    status: Optional[str] = Field(default=None, min_length=1, max_length=40)
    location: Optional[str] = Field(default=None, min_length=1, max_length=100)

    @field_validator("name", "device_type", "status", "location", mode="before")
    @classmethod
    def trim_optional_text(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("Text fields cannot be blank.")
        return value


class DeviceResponse(DeviceFields):
    id: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


devices: dict[int, DeviceResponse] = {
    1: DeviceResponse(
        id=1,
        name="Core Router 01",
        device_type="router",
        status="online",
        location="North Data Center",
    ),
    2: DeviceResponse(
        id=2,
        name="Access Switch 12",
        device_type="switch",
        status="maintenance",
        location="Building A",
    ),
}


def unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    try:
        claims = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp"]},
        )
    except InvalidTokenError as exc:
        raise unauthorized() from exc

    subject = claims.get("sub")
    if subject != TRAINING_USERNAME:
        raise unauthorized()
    return subject


def get_device_or_404(device_id: int) -> DeviceResponse:
    device = devices.get(device_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found.")
    return device


@app.post("/auth/token", response_model=TokenResponse, tags=["authentication"])
async def create_access_token(form: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    valid_user = form.username == TRAINING_USERNAME
    valid_password = password_hasher.verify(form.password, TRAINING_PASSWORD_HASH)
    if not (valid_user and valid_password):
        raise unauthorized()

    expires_at = datetime.now(timezone.utc) + TOKEN_LIFETIME
    token = jwt.encode(
        {"sub": TRAINING_USERNAME, "exp": expires_at},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )
    return TokenResponse(access_token=token)


@app.get("/devices", response_model=list[DeviceResponse], tags=["devices"])
async def list_devices() -> list[DeviceResponse]:
    return list(devices.values())


@app.get("/devices/{device_id}", response_model=DeviceResponse, tags=["devices"])
async def read_device(device_id: int) -> DeviceResponse:
    return get_device_or_404(device_id)


@app.post(
    "/devices",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["devices"],
)
async def create_device(
    payload: DeviceCreate,
    _current_user: str = Depends(get_current_user),
) -> DeviceResponse:
    next_id = max(devices, default=0) + 1
    device = DeviceResponse(id=next_id, **payload.model_dump())
    devices[next_id] = device
    return device


@app.put("/devices/{device_id}", response_model=DeviceResponse, tags=["devices"])
async def replace_device(
    device_id: int,
    payload: DeviceReplace,
    _current_user: str = Depends(get_current_user),
) -> DeviceResponse:
    get_device_or_404(device_id)
    device = DeviceResponse(id=device_id, **payload.model_dump())
    devices[device_id] = device
    return device


@app.patch("/devices/{device_id}", response_model=DeviceResponse, tags=["devices"])
async def update_device(
    device_id: int,
    payload: DevicePatch,
    _current_user: str = Depends(get_current_user),
) -> DeviceResponse:
    current = get_device_or_404(device_id)
    changes = payload.model_dump(exclude_unset=True)
    if not changes or any(value is None for value in changes.values()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide at least one non-null field to update.",
        )
    updated = current.model_dump() | changes
    device = DeviceResponse(**updated)
    devices[device_id] = device
    return device


@app.delete("/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["devices"])
async def delete_device(
    device_id: int,
    _current_user: str = Depends(get_current_user),
) -> Response:
    get_device_or_404(device_id)
    del devices[device_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
